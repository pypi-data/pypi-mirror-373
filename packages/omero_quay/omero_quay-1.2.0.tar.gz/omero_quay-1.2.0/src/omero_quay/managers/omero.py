"""OMERO operations"""

from __future__ import annotations

import logging
from collections import defaultdict
from pathlib import Path
from random import randint
from uuid import uuid1

import Ice
import lxml
import ome_types.model as mod
from ezomero import post_map_annotation
from Ice import ObjectNotExistException
from ome_types import from_xml, to_xml, validate_xml
from ome_types.model.map import M, Map
from omero.gateway import TagAnnotationWrapper

# from omero import ApiUsageException
from omero_quay.core.connect import (
    omero_conn,
    omero_nolog_cli,
    omero_sudo_cli,
    omero_sudo_conn,
)
from omero_quay.core.manifest import (
    Image,
    Manifest,
)
from omero_quay.core.utils import (
    find_by_id,
    get_class_mappings,
    get_identifiers,
    isa_from_isaobject,
)
from omero_quay.managers.manager import Manager

log = logging.getLogger(__name__)

ann_map = {
    "file_annotation": mod.FileAnnotation,
    "tag_annotation": mod.TagAnnotation,
    "map_annotation": mod.MapAnnotation,
    "comment_annotation": mod.CommentAnnotation,
}


def rand_ome_id():
    return randint(2**20, 2**30)


class OmeroManager(Manager):
    """
    This manager should not create objects in omero, this is deferred to omero transfer


    """

    def __init__(self, conf: dict, manifest: Manifest):
        super().__init__(
            conf,
            manifest,
            scheme="omero",
        )
        self.omes = []
        self.ome_user = None
        self._conn = None
        self._type_mapping = get_class_mappings("ome")
        self.stale_annotations = []  # list of omero ids

        self.log.info("Treating manifest with manager %s", self.manager)

    def __enter__(self):
        super().__enter__()
        try:
            self._conn = omero_conn(self.conf)
        except Ice.Exception:
            self._conn = None
            self.log.info("No connection with an OMERO server")

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._conn is not None:
            self._conn.__exit__(exc_type, exc_value, traceback)
        super().__exit__(exc_type, exc_value, traceback)

    @property
    def isaobjects(self):
        return (
            self.manifest.investigations
            + self.manifest.studies
            + self.manifest.assays
            + self.manifest.images
        )

    @property
    def conn(self):
        if self._conn and not self._conn.isConnected():
            self._conn.connect()
        return self._conn

    def check_omero_server(func):
        def wrapped(self, *args, **kwargs):
            if self._conn is None:
                return None
            try:
                return func(self, *args, **kwargs)
            except Ice.Exception as e:
                self.log.error("No connection with an OMERO server", exc_info=e)
                return None

        return wrapped

    def crud(self):
        if self.trgt_store.host != self.conf["omero"]["OMERO_HOST"]:
            self.log.info("This is a local omero, skipping crud")
            return
        super().crud()

    @check_omero_server
    def transfer(self):
        """
        Uses the (augmented) omes created by the `parse` method to import data in omero
        """

        if self.trgt_store.host != self.conf["omero"]["OMERO_HOST"]:
            self.log.info("This is a local omero, skipping transfer")
            return

        for isaobject, ome, duplicates in self.omes:
            log.info("OME_Experimenter_Groups: %s ", ome.experimenter_groups)

            ome_ = ome.copy()
            for image in duplicates:
                ome_.images.remove(image)
            self._write_ome(isaobject, ome_, out="transfer.xml")
            group_name = ome.experimenter_groups[0].name
            data_path = self.absolute_path(isaobject, self.trgt_store.id)
            self.log.info(
                "Importing %s in omero from path %s for user %s",
                isaobject.name,
                data_path,
                isaobject.owner,
            )
            cli = omero_sudo_cli(
                self.conf,
                self.manager,
                opts=["--group", group_name],
            )
            self.log.info(
                "Importing %s in omero from path %s", isaobject.name, data_path
            )
            try:
                cli.invoke(
                    [
                        "transfer",
                        "unpack",
                        "--merge",
                        "--ln_s_import",
                        "--folder",
                        data_path.as_posix(),
                    ],
                    strict=True,
                )
                self._update(isaobject)
            except Exception as e:
                self.log.error("Import failed ", exc_info=e)
            finally:
                path = (
                    self.absolute_path(isaobject, self.trgt_store.id) / "transfer.xml"
                )
                path.unlink()

    @check_omero_server
    def pack(self, isaobject):
        ome_id = isaobject.ome_id
        obj_t = self.type_mapping(isaobject)
        ome_object_str = f"{obj_t}:{ome_id}:"
        path = self.absolute_path(isaobject, self.srce_store.id)
        cli = omero_sudo_cli(self.conf, self.manager)
        cli.invoke(
            ["transfer", "pack", "--binaries", "none", ome_object_str, path.as_posix()],
            strict=True,
        )
        (Path(path) / "transfer.xml").copy(Path(path) / "ome.xml")

        isaobject.importlink = None

    @check_omero_server
    def type_mapping(self, isaobject):
        return self._type_mapping[isaobject.__class__.__name__]

    @check_omero_server
    def cleanup(self):
        # rempove root from users
        self.log.info("Cleaning up stale annotations %s", self.stale_annotations)
        self.stale_annotations = list(set(self.stale_annotations))
        if self.stale_annotations:
            self.log.info("Cleaning up annotations %s", self.stale_annotations)
            self.conn.deleteObjects("Annotation", self.stale_annotations, wait=True)
        for investigation in self.manifest.investigations:
            if targeted_user := self.conf["omero"].get("OMERO_ADMIN"):
                group = self._exists(investigation)
                if group:
                    self.log.info(
                        "Deleting %s user in group %s", targeted_user, group.getName()
                    )
                    cli = omero_sudo_cli(self.conf, self.manager)
                    cli.invoke(
                        [
                            "user",
                            "leavegroup",
                            group.getName(),
                            "--name=" + targeted_user,
                        ],
                        strict=True,
                    )

    def register(self, isaobject):
        ome = self._get_ome(isaobject)
        duplicates = self._build_ome(isaobject, ome)
        self.omes.append((isaobject, ome, duplicates))

    def _get_ome(self, isaobject):
        user_name = self.manager
        path = self.absolute_path(isaobject, self.trgt_store.id)
        self.log.info("Preparing data import from %s for user %s", path, user_name)
        if not path:
            msg = f"No filesystem path was found for {isaobject.name}"
            self.log.error(msg)
            raise ValueError(msg)
        try:
            ome_xml = path / "ome.xml"
            lock_file = path / "transfer.xml.lock"
        except TypeError as e:
            self.log.error("wrong path somehow, %s, urls: %s", path, isaobject.urls)
            raise e
        if lock_file.exists():
            msg = f"omero transfer prepare already processing {path}"
            self.log.info(msg)
            raise OSError(msg)
        if ome_xml.exists():
            if self.conf["omero"].get("USE_CACHE"):
                try:
                    self.log.info("Using cached ome.xml")
                    with Path(ome_xml).open("r+b") as fh:
                        return from_xml(fh)
                except (ValueError, lxml.etree.XMLSyntaxError):
                    self.log.info("Can't use cached ome.xml, looks corrupted")
            self.log.info("Removing old ome_xml")
            ome_xml.unlink()
        cli = omero_nolog_cli()

        lock_file.touch()
        transfer_xml = path / "transfer.xml"
        if transfer_xml.exists():
            transfer_xml.unlink()
        try:
            cli.invoke(["transfer", "prepare", path.as_posix()], strict=True)
            (path / "transfer.xml").rename(ome_xml)
            with ome_xml.open("r+b") as fh:
                return from_xml(fh)
        except (ValueError, lxml.etree.XMLSyntaxError) as e:
            if ome_xml.exists():
                ome_xml.unlink()
            # file gets corrupted some times
            raise e
        finally:
            lock_file.unlink()

    @check_omero_server
    def _find_by_id(self, isaobject):
        otype = self.type_mapping(isaobject)
        if isaobject.ome_id is not None:
            obj = self.conn.getObject(otype, isaobject.ome_id)
            if obj:
                self.log.debug("Found object %s by id", isaobject.name)
                return obj
        return False

    @check_omero_server
    def _find_by_path(self, isaobject):
        otype = self.type_mapping(isaobject)
        investigation, study, assay = isa_from_isaobject(self.manifest, isaobject)
        if otype != "ExperimenterGroup":
            group = self._exists(investigation)
            if not group:
                self.log.warning(
                    "Can't find investigation %s as a group in OMERO",
                    investigation.name,
                )
                return False
            opts = {"group": group.id}
        else:
            opts = {}
            group = None
        attributes = {"name": isaobject.name}

        if isinstance(isaobject, Image):
            dataset = self._exists(assay)
            if dataset:
                opts["dataset"] = dataset.id

        if study and isaobject != study:
            project = self._exists(study)
            if project:
                opts["project"] = project.id

        self.log.debug("omero search query: opts: %s, attributes: %s", opts, attributes)
        with omero_conn(self.conf) as conn:
            if group:
                conn.SERVICE_OPTS.setOmeroGroup(group.id)
            objects = list(conn.getObjects(otype, opts=opts, attributes=attributes))
            conn.SERVICE_OPTS.setOmeroGroup(-1)

        if len(objects) == 1:
            local_obj = objects[0]
            self.log.debug("Found object %s by path", isaobject.name)
            return local_obj
        if len(objects) > 1:
            self.log.error(
                "There are multiple %s named %s in group %s",
                otype,
                isaobject.name,
                investigation.name,
            )
        else:
            self.log.info("%s %s not found by its path", otype, isaobject.name)

        return False

    @check_omero_server
    def _find_by_foreign_ids(self, isaobject):
        otype = self.type_mapping(isaobject)
        ids = get_identifiers(isaobject)
        for key, value in ids.items():
            try:
                objects = self.conn.getObjectsByMapAnnotations(
                    otype, key=key, value=str(value), ns="quay"
                )
                obj = next(iter(objects))
            except (ObjectNotExistException, StopIteration, ValueError):
                continue
            self.log.info("Found object %s by it's foreign key %s", isaobject.name, key)
            break
        else:
            obj = False
        return obj

    def _create(self, isaobject):
        """Does nothing but log"""
        self.log.debug("%s will be created in omero", isaobject.name)

    @check_omero_server
    def _update(self, isaobject):
        otype = self.type_mapping(isaobject)
        if otype == "ExperimenterGroup":
            self.log.info("Not omero data clerk job")
            return
        localobject = self._exists(isaobject)
        if not localobject:
            self.log.info(
                "Object %s of type  %s has no mapping in omero",
                isaobject.name,
                type(isaobject),
            )
            return
        omero_id = localobject.getId()
        self.log.info("Updating ome_id for %s %s", otype, isaobject.name)
        isaobject.ome_id = omero_id
        ids = get_identifiers(isaobject)
        inv = self.get_parent_investigation(isaobject)
        with omero_sudo_conn(self.conf, isaobject.owner, inv.name) as conn:
            stale_map_anns = post_unique_map_annotation(
                conn, otype, omero_id, ids, ns="quay"
            )
            duplicate_tags = deduplicate_tags(conn, otype, omero_id)
            self.stale_annotations.extend(stale_map_anns + duplicate_tags)
            self.log.info("%d Stale annotations", len(self.stale_annotations))

        localobject.name = isaobject.name

    @check_omero_server
    def _delete(self, isaobject):
        if isaobject.id not in self.mapping:
            msg = f"object {isaobject.name} not found in mapping, can't delete"
            raise KeyError(msg)
        obj = self.mapping[isaobject.id]
        otype = obj.__class__.__name__

        self.conn.deleteObjects(
            otype,
            [obj],
            deleteAnns=False,
            deleteChildren=False,
            dryRun=False,
            wait=False,
        )

    def _build_ome(self, isaobject, ome):
        self.log.info("Updating ome-cli-transfer xml for %s", isaobject.name)
        duplicates = []
        paths = get_image_paths(ome)
        investigation, study, assay = isa_from_isaobject(self.manifest, isaobject)
        ome.experimenter_groups = [
            mod.ExperimenterGroup(id=rand_ome_id(), name=investigation.name)
        ]

        for ome_image in ome.images:
            for project in ome.projects:
                if project.id == f"Project:{study.ome_id}":
                    break
            else:
                if study.ome_id is None:
                    study.ome_id = rand_ome_id()
                project = mod.Project(id=f"Project:{study.ome_id}", name=study.name)
                ome.projects.append(project)
                self._annotate(study, ome, project)

            for dataset in ome.datasets:
                if dataset.id == f"Dataset:{assay.ome_id}":
                    break
            else:
                if assay.ome_id is None:
                    assay.ome_id = rand_ome_id()
                dataset = mod.Dataset(id=f"Dataset:{assay.ome_id}", name=assay.name)
                project.dataset_refs.append(mod.DatasetRef(id=dataset.id))
                ome.datasets.append(dataset)
                self._annotate(assay, ome, dataset)

            assay_path = self.absolute_path(assay, self.trgt_store.id)
            image_path = assay_path / Path(paths[ome_image.id])
            url = f"file://{image_path}"
            for image in self.manifest.images:
                if url in image.urls:
                    break
            else:
                image = Image(
                    id=f"img_{uuid1()}",
                    name=ome_image.name,
                    owner=investigation.owner,
                    urls=[url],
                )
                image.parents.append(assay.id)
                assay.images.append(image.id)
                self.manifest.images.append(image)
            if (
                self.conn is not None
                and self._exists(image)
                and (image not in duplicates)
            ):
                duplicates.append(ome_image)

            for annotation in assay.quay_annotations:  # added by Marc
                if annotation not in image.quay_annotations:
                    image.quay_annotations.append(annotation)

            self._annotate(image, ome, ome_image)
            dataset.image_refs.append(mod.ImageRef(id=ome_image.id))

        if duplicates:
            self.log.warning("Found %d existing images", len(duplicates))
            return duplicates
        return []

    @check_omero_server
    def _annotate(self, isaobject, ome=None, localobject=None):
        mmap = [M(k=k, value=str(v)) for k, v in get_identifiers(isaobject).items()]
        ann = mod.MapAnnotation(
            id=f"Annotation:{rand_ome_id()}", value=Map(ms=mmap), namespace="quay"
        )
        ome.structured_annotations.append(ann)
        localobject.annotation_refs.append(mod.AnnotationRef(id=ann.id))

        for ann_id in isaobject.quay_annotations:
            ann = find_by_id(ann_id, self.manifest.quay_annotations)
            ome_kls = ann_map[ann.ann_type]

            match ome_kls:
                case mod.MapAnnotation:
                    mmap = [
                        M(k=kv.key, value=str(kv.value))
                        for kv in ann.kv_pairs
                        if kv.value
                    ]

                    local_ann = mod.MapAnnotation(
                        id=f"Annotation:{rand_ome_id()}",
                        value=Map(ms=mmap),
                        namespace="quay",
                    )
                    ome.structured_annotations.append(local_ann)
                    localobject.annotation_refs.append(
                        mod.AnnotationRef(id=local_ann.id)
                    )
                case mod.TagAnnotation | mod.CommentAnnotation:
                    local_ann = ome_kls(
                        id=f"Annotation:{rand_ome_id()}",
                        value=ann.value,
                        namespace="quay",
                    )
                    ome.structured_annotations.append(local_ann)
                    localobject.annotation_refs.append(
                        mod.AnnotationRef(id=local_ann.id)
                    )

    @check_omero_server
    def update_manifest(self, isaobject, ome):
        """ """
        raise NotImplementedError

    def _write_ome(self, isaobject, ome, out="transfer.xml"):
        path = self.absolute_path(isaobject, self.trgt_store.id) / out
        if path.exists():
            path.unlink()
        xml_string = to_xml(ome)
        validate_xml(xml_string)

        with path.open("w+", encoding="utf-8") as th:
            th.write(xml_string)


def get_image_paths(ome):
    """
    Retrieves original import paths from annotations in an OME object
    generated by omero-cli-transfer
    """
    xml_anns = {
        ann.id: ann.value.any_elements[0].children[0].text
        for ann in ome.structured_annotations.xml_annotations
    }

    original_paths = {}
    for img in ome.images:
        for ref in img.annotation_refs:
            if ref.id in xml_anns:
                original_paths[img.id] = xml_anns[ref.id]
                break
    if len(original_paths) != len(ome.images):
        msg = f"Not all paths found for images {', '.join([img.name for img in ome.images])} "
        raise ValueError(msg)

    return original_paths


def deduplicate_map_annotations(conn, otype, omero_id, ns):
    solidified = {}
    to_delete = []

    # get the object again to avoid connection issues
    omero_object = conn.getObject(otype, omero_id)
    if omero_object is None:
        log.error(
            "Omero %s:%d was not found for annotations, check permissions maybe",
            otype,
            omero_id,
        )
        return []
    # Deduplicate
    for ann in omero_object.listAnnotations(ns):
        if hasattr(ann, "getMapValueAsMap"):
            _map = ann.getMapValueAsMap()
            solidified.update(_map)
            to_delete.append(ann.id)

    post_map_annotation(conn, otype, omero_object.getId(), solidified, ns)
    return to_delete


def deduplicate_tags(conn, otype, omero_id):
    tag_d = defaultdict(set)
    existings = {}
    # get the object again to avoid connection issues
    omero_object = conn.getObject(otype, omero_id)
    if omero_object is None:
        log.error(
            "Omero %s:%d was not found for annotations, check permissions maybe",
            otype,
            omero_id,
        )
        return []

    to_delete = []
    for tag in omero_object.listAnnotations():
        if isinstance(tag, TagAnnotationWrapper):
            text = tag.getValue()
            existing = next(
                iter(conn.getObjects("TagAnnotation", attributes={"textValue": text}))
            )
            tag_d[text] = tag_d[text].union({tag.id})
            existings[text] = existing

    for text in tag_d:
        tags, existing = tag_d[text], existings[text]
        if existing.id not in tags:
            omero_object.linkAnnotation(existing)
        to_delete.extend(list(tags - {existing.id}))
    return to_delete


def post_unique_map_annotation(conn, otype, omero_id, mapping, ns):
    solidified = {}
    to_delete = []

    # get the object again to avoid connection issues
    omero_object = conn.getObject(otype, omero_id)
    if omero_object is None:
        log.error(
            "Omero %s:%d was not found for annotations, check permissions maybe",
            otype,
            omero_id,
        )
        return []
    # Deduplicat
    for ann in omero_object.listAnnotations(ns):
        if hasattr(ann, "getMapValueAsMap"):
            _map = ann.getMapValueAsMap()
            solidified.update(_map)
            to_delete.append(ann.id)

    # Update
    solidified.update(mapping)
    post_map_annotation(conn, otype, omero_id, solidified, ns)
    return to_delete
