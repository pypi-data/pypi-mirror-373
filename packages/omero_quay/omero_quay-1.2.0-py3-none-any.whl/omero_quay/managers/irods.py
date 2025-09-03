"""
iRODS  operations

"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from urllib.parse import urlparse

import irods.keywords as kw
from irods.access import iRODSAccess
from irods.column import Criterion
from irods.exception import (
    CAT_NO_ACCESS_PERMISSION,
    CAT_SQL_ERR,
    UNIX_FILE_CREATE_ERR,
    UNIX_FILE_OPEN_ERR,
)
from irods.models import Collection as RCollection
from irods.models import CollectionMeta, DataObjectMeta
from irods.models import DataObject as RDataObject

from omero_quay.core.connect import irods_conn, irods_sudo_conn
from omero_quay.core.manifest import (
    Assay,
    Collection,
    File,
    Investigation,
    Manifest,
)
from omero_quay.core.provenance import get_data_root
from omero_quay.core.utils import (
    get_identifiers,
    isa_from_isaobject,
)
from omero_quay.managers.manager import Manager

log = logging.getLogger(__name__)


class iRODSManager(Manager):
    """Parses manifest in iRODS
    example:

    .. code-block:: [python]

        dry_run = False
        ...
        with iRODSManager(manifest) as rodsmngr:
            rodsmngr.parse()
            # check every thing is ok
            print(rodsmngr)
            if not dry_run:
                rodsmngr.transfer()
    """

    def __init__(self, conf: dict, manifest: Manifest):
        """

        required conf entries

        conf["irods"]['IRODS_HOST']
        conf["irods"]['IRODS_PORT']
        conf["irods"]['IRODS_ADMIN']
        conf["irods"]['IRODS_ZONE']
        conf["irods"]['IRODS_ADMIN_PASS']

        """
        super().__init__(
            conf,
            manifest,
            scheme="irods",
        )
        self.session = None
        self.srce_resc_name = self.srce_store.resc
        self.trgt_resc_name = self.trgt_store.resc

        self.srce_file_root = get_data_root(
            self.manifest,
            self.srce_store.id,
            scheme="file",
            template=True,
        )

        self.srce_irods_root = get_data_root(
            self.manifest,
            self.srce_store.id,
            scheme="irods",
            template=True,
        )

        if self.srce_irods_root is None:
            # Using target irods resource to put staged user data
            self.srce_irods_root = get_data_root(
                self.manifest,
                self.trgt_store.id,
                scheme="irods",
                template=True,
            )
            # again ...
            if self.srce_irods_root is None:
                msg = "There are no irods resources described in the manifest's provenance "
                raise ValueError(msg)

        # The importlink paths in the initial manifest
        # Need to be mapped to the underlying
        # unix filesystem
        # That's the case for samba
        self.needs_mapping = self.srce_store.scheme not in ("irods", "file", "omero")
        self.log.info("manifest needs mapping: %s", self.needs_mapping)
        # data is on the drive, we have an irods resc
        # at the source that we can register to
        # and we are not directly using irods
        # that's the case for samba or files written directly on
        # the disc
        self.needs_register = (
            self.srce_irods_root is not None
            and (self.srce_store.scheme != "irods")
            and not self.srce_store.is_isa
        )
        self.log.info("manifest needs register: %s", self.needs_register)

        # data is in irods user space, not yet in ISA hierarchy
        # transfer will apply a copy from source to destination
        self.needs_copy = not self.srce_store.is_isa and (
            self.srce_store.scheme == "irods"
        )
        self.log.info("manifest needs copy: %s", self.needs_copy)

        # Data is already in an ISA hiererarchy
        # and We have a source irods store
        # that is different from the target store
        self.needs_replicate = (
            self.srce_store.is_isa
            and (self.srce_store.scheme == "irods")
            and (self.srce_resc_name != self.trgt_resc_name)
        )
        self.log.info("manifest needs replicate: %s", self.needs_replicate)

        # Data is not yet in irods but already formatted as
        # an isa hierarchy.
        self.needs_put = self.srce_store.is_isa and (self.srce_store.scheme != "irods")
        self.log.info("manifest needs put: %s", self.needs_put)

    def __enter__(self):
        super().__enter__()
        self.session = irods_conn(self.conf)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)
        self.session.__exit__(exc_type, exc_value, traceback)

    def register(self, isaobject):
        for importlink in isaobject.importlinks:
            self._register(isaobject, importlink)

    def _register(self, isaobject, importlink):
        """

        Parses a collection recursively into an ISA hierarchy of objects.

        Data pointed to by an url in the assay importlinks is imported
        """
        link = urlparse(importlink.srce_url)
        if not any(
            (self.needs_register, self.needs_mapping, self.needs_copy, self.needs_put)
        ):
            self.log.info("No path manipulation needed, skipping self.register")
            return

        if self.needs_put:
            self._prepare_importlink(isaobject, importlink)
            return

        # # let's fix permissions
        user = self.manager
        with irods_sudo_conn(self.conf, user) as sess:
            irods_parent = Path(link.path).parent.as_posix()
            if not self.needs_put and not sess.collections.exists(irods_parent):
                # Create collections, incl. parents, from irods_path up
                coll = sess.collections.create(irods_parent, recurse=True)
                self.log.info("Created %s", coll)
            else:
                coll = sess.collections.get(irods_parent)
            try:
                inherit = iRODSAccess("inherit", coll)
                sess.acls.set(inherit)
                acl = iRODSAccess("own", coll, user, user_type="rodsuser")
                sess.acls.set(acl)
                if admin := self.conf["irods"]["IRODS_ADMIN"]:
                    acl = iRODSAccess("own", coll, admin, user_type="rodsadmin")
                    sess.acls.set(acl)
            except TypeError:
                self.log.info("Error when trying to set acl for user %s", user)
            except CAT_NO_ACCESS_PERMISSION:
                self.log.error(
                    "WARNING: Could not set acl for collection %s", irods_parent
                )
        if self.needs_mapping:
            try:
                if client_root := get_data_root(
                    self.manifest,
                    self.srce_store,
                    scheme="smb",  # For now ...
                    template=True,
                ):
                    rel_path = Path(link.path).relative_to(client_root)
            except ValueError as e:
                msg = (
                    "inconsistency between the importlink path and the client data root"
                )
                raise ValueError(msg) from e

            unix_path = Path(self.srce_file_root) / rel_path
            irods_path = Path(self.srce_irods_root) / rel_path
        elif self.srce_store.scheme != "irods":
            unix_path = link.path
            rel_path = Path(unix_path).relative_to(self.srce_file_root)
            irods_path = Path(self.srce_irods_root) / rel_path
        elif self.srce_store.scheme == "irods":
            irods_path = link.path
            rel_path = Path(irods_path).relative_to(self.srce_irods_root)
            unix_path = Path(self.srce_file_root) / rel_path

        if self.needs_register:
            with irods_conn(self.conf) as sess:
                self.log.info(
                    "registering %s to %s on resc %s",
                    unix_path,
                    irods_path,
                    self.trgt_resc_name,
                )
                options = {
                    kw.RESC_NAME_KW: self.srce_resc_name,
                    kw.RECURSIVE_OPR__KW: "recursiveOpr",
                    kw.FORCE_FLAG_KW: "forceFlag",  # force update #
                }
                try:
                    # There
                    sess.collections.register(unix_path, irods_path, **options)
                except UNIX_FILE_CREATE_ERR as e:
                    self.log.error(
                        "WARNING: Error registering Path : %s in collection %s",
                        unix_path,
                        irods_path,
                    )
                    pth = Path(unix_path).relative_to(self.srce_file_root)
                    msg = f"There was an issue while registering {pth} in {isaobject.name}."
                    raise OSError(msg) from e

        with irods_sudo_conn(self.conf, self.manifest.manager) as sess:
            if not sess.collections.exists(irods_path):
                msg = f"could not find link {link.path} in irods"
                self.log.error(msg)
                raise OSError(msg)

        self._prepare_importlink(isaobject, importlink)
        return

    def transfer(self):
        """
        Moves data_objects from source to destination as mapped in
        `self.destinations` and according to input (srce_store)
        and output (manifest.provenance.trgt_store) resources.

        the manager will copy data objects with the -F (force copy) flag, equivalent
        to `icp -f srce_store trgt_store`

        """
        options = {
            kw.FORCE_FLAG_KW: "forceFlag",
            kw.RESC_NAME_KW: self.trgt_resc_name,
        }
        for _, destinations in self.destinations.items():
            with irods_sudo_conn(self.conf, self.manager) as sess:
                for srce, dest in destinations.items():
                    if sess.collections.exists(srce):
                        # srce is a collection
                        self.log.warning(
                            "Should not have a collection as a source in manager's destinations"
                        )
                        continue

                    if sess.collections.exists(dest):
                        self.log.warning(
                            "Should not have a collection as a target in manager's destinations "
                        )
                        dest = (Path(dest) / Path(srce).name).as_posix()  # noqa:PLW2901

                    if self.needs_copy:
                        self.log.info("copying  %s to %s", srce, dest)
                        sess.data_objects.copy(srce, dest, **options)
                        continue

                    if self.needs_replicate:
                        self.log.info(
                            "replicating data from resource %s to %s",
                            self.srce_store.resc,
                            self.trgt_store.resc,
                        )
                        sess.data_objects.replicate(
                            srce, self.trgt_store.resc, **options
                        )
                        continue

                    if self.needs_put:
                        self.log.info(
                            "putting data from file store %s to irods store %s",
                            self.srce_store.id,
                            self.trgt_store.id,
                        )
                        sess.data_objects.put(srce, dest, **options)

                        continue

    def annotate(self):
        raise NotImplementedError

    def _delete(self, isaobject):
        if localobject := self._exists(isaobject):
            if isinstance(isaobject, Collection):
                self.session.collections.remove(localobject.path, recurse=True)
            elif isinstance(isaobject, File):
                self.session.data_objects.unlink(localobject.path)
        else:
            self.log.info("Object %s marked for deletion not found", isaobject.name)

    def _update(self, isaobject):
        localobject = self._exists(isaobject)
        if not localobject:
            msg = (
                f"Object {isaobject.name} of type "
                " {type(isaobject)} has no mapping in irods"
            )
            raise ValueError(msg)

        if isaobject.irods_id != localobject.id:
            self.log.debug(
                "updating Id discrepancy between %s %s and iRODS %s %s",
                isaobject.__class__.__name__,
                isaobject.name,
                localobject.__class__.__name__,
                localobject.name,
            )

        trgt_path = self.absolute_path(isaobject, self.trgt_store.id)
        if localobject.path != trgt_path.as_posix():
            self.log.info(
                "Planning to move %s from %s to %s",
                localobject.name,
                localobject.path,
                trgt_path,
            )
            self.destinations[isaobject.owner][localobject.path] = trgt_path

        self._set_ids_metadata(isaobject, localobject)

    def _set_ids_metadata(self, isaobject, localobject):
        self.log.info("Updating irods id for %s", isaobject.name)
        isaobject.irods_id = localobject.id
        for key, val in get_identifiers(isaobject).items():
            if key in localobject.metadata.keys():  # noqa:SIM118
                old = localobject.metadata.get_all(key)[-1]
                if old.value != str(val):
                    self.log.info("Updating %s for object %s", key, isaobject.name)
                    localobject.metadata.set(key, str(val))
            else:
                localobject.metadata.add(key, str(val))
                self.log.info("Setting %s for object %s", key, isaobject.name)

    def _find_by_path(self, isaobject):
        path = self.absolute_path(isaobject, self.trgt_store.id).as_posix()
        if isaobject.owner is not None:
            session = irods_sudo_conn(self.conf, isaobject.owner)
        else:
            session = self.session

        if isinstance(isaobject, Collection):
            if session.collections.exists(path):
                return session.collections.get(path)

            return False

        if isinstance(isaobject, File):
            if session.data_objects.exists(path):
                return session.data_objects.get(path)
            return False

        msg = (
            "Only objects inheritating from File or Collection can be searched by path"
        )
        raise ValueError(msg)

    def _find_by_id(self, isaobject):
        if isaobject.owner is not None:
            session = irods_sudo_conn(self.conf, isaobject.owner)
        else:
            session = self.session

        if isaobject.irods_id is None:
            return False

        if isinstance(isaobject, Collection):
            results = (
                session.query(RCollection.name)
                .filter(Criterion("=", RCollection.id, isaobject.irods_id))
                .all()
            )
            if results:
                (name,) = results[0].values()
                return session.collections.get(name)
            return False

        if isinstance(isaobject, File):
            results = (
                session.query(RDataObject.path)
                .filter(Criterion("=", RDataObject.id, isaobject.irods_id))
                .all()
            )
            if results:
                (name,) = results[0].values()
                return session.data_objects.get(name)
            return False

        msg = "Only objects inheritating from File or Collection can be searched"
        raise ValueError(msg)

    def _find_by_foreign_ids(self, isaobject):
        if isaobject.owner is not None:
            session = irods_sudo_conn(self.conf, isaobject.owner)
        else:
            session = self.session
        ids = get_identifiers(isaobject)

        if isinstance(isaobject, Collection):
            for key, value in ids.items():
                results = (
                    session.query(RCollection.name)
                    .filter(Criterion("=", CollectionMeta.name, key))
                    .filter(Criterion("=", CollectionMeta.value, value))
                ).all()
                if results:
                    (path,) = results[0].values()
                    self.log.info("Found object %s by it's key %s", isaobject.name, key)
                    return session.collections.get(path)
            return False

        if isinstance(isaobject, File):
            for key, value in ids.items():
                results = (
                    self.session.query(RDataObject.path)
                    .filter(Criterion("=", DataObjectMeta.name, key))
                    .filter(Criterion("=", DataObjectMeta.value, value))
                ).all()
                if results:
                    (path,) = results[0].values()
                    return self.session.data_objects.get(path)
            return False

        msg = "Only objects inheritating from File or Collection can be searched"
        raise ValueError(msg)

    def _create(self, isaobject: Collection):
        if isinstance(isaobject, Investigation):
            self.log.warning("investigation %s can't be created by a data clerk")

        elif isinstance(isaobject, Collection):
            self._create_coll(isaobject)

    def _create_coll(self, isaobject):
        """Creates the collection in iRODS and sets acls"""
        with irods_sudo_conn(self.conf, self.manager) as sess:
            path = self.absolute_path(isaobject, self.trgt_store.id).as_posix()
            has_coll = sess.collections.exists(path)
            if has_coll:
                coll = sess.collections.get(path)
                if not _check_acl(isaobject.owner, self.session, coll):
                    err_msg = f"The isaobject {isaobject.name} already exists, user {isaobject.owner} can't modify it"
                    raise ValueError(err_msg)

                self.log.info(
                    "collection %s already exists, user %s can modify it",
                    isaobject.name,
                    isaobject.owner,
                )
            else:
                try:
                    coll = sess.collections.create(path)
                except CAT_SQL_ERR as e:
                    self.log.error("error creating collection at %s", path, exc_info=e)
                    raise e

            self._set_ids_metadata(isaobject, coll)

            acl = iRODSAccess("own", coll.path, isaobject.owner, user_type="rodsuser")
            sess.acls.set(acl)
            inh_acl = iRODSAccess("inherit", coll.path)
            sess.acls.set(inh_acl)

    def _prepare_importlink(self, assay, importlink):
        """Creates the assay collection in iRODS and moves the content pointed
        by importlink there.

        Subdirectories are suffixed to the file name
        """
        for isao in isa_from_isaobject(self.manifest, assay):
            if not self._exists(isao) and isao not in self.created:
                self.created.append(isao)
            elif isao not in self.updated:
                self.updated.append(isao)

        link_path = urlparse(importlink.srce_url).path
        if not self.needs_put:
            to_import = self.session.collections.get(link_path)
        else:
            if self.srce_store.is_isa:
                to_import = self.absolute_path(assay, self.srce_store.id)

            elif self.needs_mapping:
                client_data_root = get_data_root(
                    self.manifest,
                    self.srce_store.id,
                    scheme=self.srce_store.scheme,
                    template=True,
                )
                file_data_root = get_data_root(
                    self.manifest,
                    self.srce_store.id,
                    scheme="file",
                    template=True,
                )

                to_import = Path(file_data_root) / Path(link_path).relative_to(
                    client_data_root
                )
            else:
                file_data_root = get_data_root(
                    self.manifest,
                    self.srce_store.id,
                    scheme="file",
                    template=True,
                )

        # assay.importlink.trgt_url = f"irods://{path}"
        # concatenate subdirectories and add to move list
        self.log.info("Walking through assay")
        self._walk_assay(assay, to_import)

    def prepare_datalink(self, datalink):
        """Moves a single file or the files in the directory to the assay

        Sub-directories are ignored, destination must already exist
        """
        raise NotImplementedError

    def _walk_assay(self, assay: Assay, collection: str):
        if not self.trgt_store.is_isa:
            msg = f"Target stores MUST be isa for now {self.trgt_store.id} is not"
            raise ValueError(msg)

        # Source data is not on irods
        if self.needs_put:
            for current_dir, _, files in os.walk(collection):
                self._walk_put(assay, collection, current_dir, files)
            return

        for subcol, _, data_objects in collection.walk():
            self._walk_col2col(assay, subcol, data_objects)

    def _walk_put(
        self,
        isaobject: Collection,
        collection: str,
        current_dir: str,
        files: list(str),
    ):
        # self.log.debug("Destinations: %s", self.destinations)
        trgt_col_path = self.absolute_path(isaobject, self.trgt_store.id)

        rel_dir_path = "_".join(Path(current_dir).relative_to(collection).parts)
        for file in files:
            srce_path = Path(collection) / current_dir / file
            if rel_dir_path:  # concatenate hierarchy
                trgt_do_path = trgt_col_path / f"{rel_dir_path}_{file}"
            else:
                trgt_do_path = trgt_col_path / file
            self.destinations[isaobject.owner].update(
                {srce_path.as_posix(): trgt_do_path.as_posix()}
            )

            self.log.info("will put file %s to irods %s ", srce_path, trgt_do_path)

    def _walk_col2col(self, isaobject, subcol, data_objects):
        rel_col_path = "_".join(Path(subcol.name).parts)
        trgt_col_path = self.absolute_path(isaobject, self.trgt_store.id) / subcol.name

        for do in data_objects:
            srce_path = do.path
            if rel_col_path:
                trgt_do_path = trgt_col_path / f"{rel_col_path}_{do.name}"
            else:
                trgt_do_path = trgt_col_path / do.name
            self.destinations[isaobject.owner].update(
                {srce_path: trgt_do_path.as_posix()}
            )
            self.log.info(
                "will copy or move data object from %s to irods %s ",
                srce_path,
                trgt_do_path,
            )


def _check_acl(user_name, session, col, minimal="modify_object"):
    acls = session.acls.get(col)
    min_val = iRODSAccess.to_int(minimal)
    for acl in acls:
        if acl.user_type == "rodsgroup":
            members = [m.name for m in session.groups.get(acl.user_name).members]
            if user_name in members:
                return iRODSAccess.to_int(acl.access_name) >= min_val
            return False
        if acl.user_name == user_name:
            return iRODSAccess.to_int(acl.access_name) >= min_val
    return False


def put_directory(local_path, logical_path, session, **options):
    local_path = Path(local_path)
    for root, dirs, files in os.walk(local_path):
        rel_root = Path(root).relative_to(local_path)
        irods_col_path = (Path(logical_path) / local_path.name / rel_root).as_posix()
        if not session.collections.exists(irods_col_path):
            session.collections.create(irods_col_path)

        for local_file in files:
            local_file_path = (Path(root) / local_file).as_posix()
            irods_file_path = (Path(irods_col_path) / local_file).as_posix()
            try:
                session.data_objects.put(local_file_path, irods_file_path, **options)
            except UNIX_FILE_OPEN_ERR:
                log.info("File %s is opened, skipping ", irods_file_path)
        for local_dir in dirs:
            irods_dir_path = (Path(irods_col_path) / local_dir).as_posix()
            if not session.collections.exists(irods_dir_path):
                session.collections.create(irods_dir_path)
