"""
iRODS file operations

"""

from __future__ import annotations

import logging
import os
import shutil
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

from omero_quay.core.manifest import Assay, Collection, Manifest
from omero_quay.managers.manager import Manager

log = logging.getLogger(__name__)


class FSManager(Manager):
    """Parses manifest in a file system

    example:

    .. code-block:: [python]

        dry_run = False
        ...
        with FSManager(manifest) as fsmngr:
            fsmngr.parse()
            # check every thing is ok
            print(fsmngr)
            fsmngr.transfer()

    """

    scheme = "file"

    def __init__(self, conf: dict, manifest: Manifest, host: str | None = None):
        """

        required conf entries:

        conf['file']['SRCE_DIR'] # base directory at the source
        conf['file']['DEST_DIR'] # base directory at the destination
        conf['file']['copy_method'] # copy | symlink | hardlink
        """
        super().__init__(conf, manifest, scheme="file", host=host)
        self.destinations = defaultdict(dict)

    def transfer(self):
        """
        Creates the ISA hierarchy for  self.new

        Moves data_objects from source to destination as mapped in
        `self.destinations`
        """
        self.log.info("in manager transfer")

        for _, destinations in self.destinations.items():
            for srce, dest in destinations.items():
                self.__move__(srce, dest)
                self.log.debug("moved %s to %s", srce, dest)

    def __move__(self, srce, dest):
        if Path(srce).is_dir():
            msg = f"source {srce} should not be a directory"
            raise ValueError(msg)
        if Path(dest).is_dir():
            msg = f"destination {dest} should not be a directory"
            raise ValueError(msg)

        if not Path(dest).parent.exists():
            Path(dest).parent.mkdir(parents=True, exist_ok=True)
        copy_method = self.conf["file"].get("copy_method")
        if copy_method in ("copy", None):
            shutil.copy2(srce, dest)
        elif copy_method == "hardlink":
            try:
                Path(dest).hardlink_to(srce)
            except FileExistsError:
                Path(dest).unlink()
                Path(dest).hardlink_to(srce)
            except OSError as e:
                msg = """
 Choose a different data root for your transfers if you use hardlinks.
 The data source and conf['file']['DEST_DIR'] must be on the same drive"""
                self.log.error(msg, exc_info=e)
                raise e

        elif copy_method == "symlink":
            Path(dest).symlink_to(srce)

    def _delete(self, isaobject):
        if localobject := self._exists(isaobject):
            if localobject.is_dir():
                shutil.rmtree(localobject)
            else:
                localobject.unlink()

    def _update(self, isaobject):
        """Do nothing"""

    def _find_by_path(self, isaobject):
        if path_ := self.absolute_path(isaobject, self.trgt_store.id):
            path = Path(path_)
            if path.exists():
                return path
        else:
            self.log.info("No 'file' entry in %s", isaobject.name)
        return False

    def _find_by_id(self, isaobject):  # noqa:ARG002
        return False

    def _find_by_foreign_ids(self, isaobject):  # noqa:ARG002
        return False

    def _create(self, isaobject):
        if isinstance(isaobject, Collection):
            path = self.absolute_path(isaobject, self.trgt_store.id)
            isaobject.urls.append(f"file://{path}")
            Path(path).mkdir(mode=0o744, parents=True, exist_ok=True)

    def register(self, isaobject):
        for importlink in isaobject.importlinks:
            link_path = Path(urlparse(importlink.srce_url).path)
            if not link_path.exists():
                msg = f"{link_path} not found"

                raise ValueError(msg)

            if isinstance(isaobject, Assay):
                self._prepare_assay(isaobject, importlink)

    def _prepare_assay(self, assay, importlink):
        """Creates the assay collection on the filesystem and moves the content pointed
        by importlink there.

        Subdirectories are ignored
        """

        link_path = Path(urlparse(importlink.srce_url).path)
        if not link_path.exists():
            msg = f"Import path {link_path} does not exist on the host"
            raise ValueError(msg)
        for current_dir, _, files in os.walk(link_path):
            self._walk_dir(assay, link_path, current_dir, files)

    def _walk_dir(self, isaobject, directory, current_dir, files):
        trgt_dir_path = self.absolute_path(
            isaobject, self.trgt_store.id
        )  # / current_dir
        self.log.info("Target dir path %s", trgt_dir_path)
        self.log.info("Current dir path %s", current_dir)
        owner = isaobject.owner
        rel_dir_path = "_".join(Path(current_dir).relative_to(directory).parts)
        for file in files:
            srce_path = Path(directory) / current_dir / file
            if rel_dir_path:  # concatenate hierarchy
                trgt_file_path = trgt_dir_path / f"{rel_dir_path}_{file}"
            else:
                trgt_file_path = trgt_dir_path / file
                self.log.info("No concatenation for %s", trgt_file_path)
            self.destinations[owner].update(
                {srce_path.as_posix(): trgt_file_path.as_posix()}
            )
            # self.log.info("will copy file %s to file %s ", srce_path, trgt_file_path)

    def prepare_datalink(self, datalink):
        """Moves a single file or the files in the directory to the assay

        Sub-directories are ignored, destination must already exist
        """
        raise NotImplementedError

    # def _walk_study(self, study, path):
    #     stu_path = self.absolute_path(study, self.trgt_store.id)
    #     for subdir, _, files in os.walk(path):
    #         rel_path = "_".join(Path(subdir).relative_to(path).parts)
    #         if not rel_path:  # orphaned data at study root
    #             rel_path = "orphaned"

    #         abs_path = Path(stu_path) / rel_path
    #         self.destinations[study.owner].update(
    #             {path.as_posix(): abs_path.as_posix()}
    #         )

    #         assay = Assay(
    #             id=f"ass_{uuid1()}",
    #             owner=study.owner,
    #             name=rel_path,
    #             parents=[study.id],
    #             urls=[f"file://{abs_path}"],
    #         )
    #         study.children.append(assay.id)
