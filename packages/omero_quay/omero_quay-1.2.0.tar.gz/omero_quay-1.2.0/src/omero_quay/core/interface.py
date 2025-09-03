from __future__ import annotations

import logging
import os
import platform
import traceback
from datetime import datetime
from itertools import product
from pathlib import Path
from uuid import uuid1

from jinja2 import Environment, PackageLoader
from linkml_runtime.dumpers import json_dumper, yaml_dumper
from linkml_runtime.loaders import yaml_loader

from omero_quay.clients.http import (
    get_mongo_manifest,
    post_mongo_manifest,
)
from omero_quay.core.manifest import (
    Assay,
    Error,
    Image,
    Investigation,
    Manifest,
    State,
    Store,
    Study,
)
from omero_quay.core.provenance import get_data_root, get_local_provenance
from omero_quay.core.utils import find_by_id, isa_from_isaobject

log = logging.getLogger(__name__)

HOME = Path(os.environ["HOME"])


log_path = HOME / "log" / "omero_quay"

log_path.mkdir(parents=True, exist_ok=True)

jinja_env = Environment(
    loader=PackageLoader("omero_quay"),
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True,
)


class Interface:
    """Base class to interact with a manifest object"""

    def __init__(
        self,
        conf: dict,
        manifest: Manifest | None = None,
        scheme: str | None = None,
        host: str | None = None,
    ):
        log.info("using interface sub class %s", self.__class__.__name__)
        if manifest is None:
            self.manifest = Manifest(id=f"man_{uuid1()}")
            self.manager = None
            log.info("Interface %s created an empty manifest", self.__class__.__name__)
        else:
            self.manifest = manifest
            if manifest.manager:
                self.manager = manifest.manager
            else:
                manager_ = next(
                    iter(
                        filter(
                            lambda m: m.role == "manager",
                            self.manifest.members,
                        )
                    )
                )
                self.manager = manager_.name
                self.manifest.manager = self.manager

        self.conf = conf
        if self.manifest.provenance is None:
            self.manifest.provenance = get_local_provenance(self.conf)
            self.manifest.destination = get_local_provenance(self.conf)

        self.log = None
        self.setup_logging()

        self.scheme = scheme
        if self.manifest.step is None:
            self.manifest.step = 0
        self.has_db = False
        self.get_url = None
        if get_url := self.conf["quay"].get("QUAY_URL"):
            self.has_db = True
            self.post_url = f"{self.conf['quay'].get('QUAY_URL')}/mongo"
            self.get_url = get_url
        if self.has_db:
            self.record()

        # default store is the target store's host
        if host is None:
            host = platform.node()
        self.host = host
        self._state_id = f"{self.__class__.__name__}@{self.host}"

    @property
    def state(self):
        if state := find_by_id(self._state_id, self.manifest.states):
            return state
        state = State(
            id=self._state_id,
            store=self.trgt_store.id,
            timestamps=[datetime.now().isoformat()],
            host=self.host,
            scheme=self.scheme,
            status="started",
        )
        self.manifest.states.append(state)
        return state

    @state.setter
    def state(self, new):
        self.manifest.states.pop(self.manifest.states.index(self.state))
        self.manifest.states.append(new)

    def setup_logging(self):
        LOG_LEVEL = self.conf["quay"].get("LOG_LEVEL", "DEBUG")
        self.log = logging.getLogger(f"omero_quay.{self.manifest.id}")
        self.log.setLevel(LOG_LEVEL)
        log_file = log_path / f"{self.manifest.id}.log"
        if not log_file.exists():
            handler = logging.FileHandler(log_file)
            handler.setLevel(LOG_LEVEL)
            self.log.addHandler(handler)

    @classmethod
    def from_manifest_yaml(cls, conf, manifest_yml):
        with Path(manifest_yml).open("r", encoding="utf-8") as fh:
            manifest = yaml_loader.load(fh, target_class=Manifest)
        return cls(conf, manifest)

    @property
    def srce_store(self):
        if not self.manifest.route:
            return Store(
                id=f"{self.host}{self.scheme.capitalize()}",
                host=self.host,
                scheme="xlsx",
                is_isa=False,
                data_roots=[],
            )

        if self.manifest.step < len(self.manifest.route):
            return self.manifest.route[self.manifest.step]
        msg = f"Previous step was the last, current step: {self.manifest.step}, route: {self.manifest.route}"
        raise ValueError(msg)

    @property
    def trgt_store(self):
        if not self.manifest.route:
            return Store(
                id=f"{self.host}{self.scheme.capitalize()}",
                host=self.host,
                scheme=self.scheme,
                is_isa=False,
                data_roots=[],
            )
        if self.manifest.step < len(self.manifest.route):
            try:
                return self.manifest.route[self.manifest.step + 1]
            except IndexError:
                msg = f"""Previous step was the last, current step:
                 {self.manifest.step}, route: {self.manifest.route}"""
                return self.manifest.route[-1]

        raise ValueError(msg)

    def relative_path(self, isaobject):
        isa = isa_from_isaobject(self.manifest, isaobject)
        return "/".join(isao.name for isao in isa if isao is not None)

    def absolute_path(self, isaobject, store_id):
        data_root = get_data_root(self.manifest, store_id, template=True)
        return Path(data_root) / self.relative_path(isaobject)  # .as_posix()

    def set_state(self, status):
        """Set the state of the interface. Permissible values values for status:

        - started
        - changed
        - checked
        - expired
        - errored

        Args:
            status (str): The status of the item.
        """

        timestamps = [*self.state.timestamps, datetime.now().isoformat()]

        state_ = State(
            id=self._state_id,
            store=self.trgt_store.id,
            timestamps=timestamps,
            host=self.host,
            scheme=self.scheme,
            status=status,
        )
        self.state = state_

        self.log.info(
            "manager %s state set to %s",
            self.__class__.__name__,
            self.state.status,
        )

        if self.has_db:
            self.record()

    def post_manifest(self, post_url=None):
        if post_url is None:
            post_url = self.post_url
        return post_mongo_manifest(self.manifest, self.conf, post_url=post_url)

    def set_other_states(self, status, stores):
        for state, store in product(self.manifest.states[::-1], stores):
            now = datetime.now().isoformat()

            if str(state.store) == store:
                self.log.info("setting status %s for store %s", status, store)
                new_state = State(timestamps=[now], store=store, status=status)
                new_state.status = status
                self.manifest.states.remove(state)
                self.manifest.states.append(new_state)

        if self.has_db:
            self.record()

    def __enter__(self):
        if self.has_db:
            self.get_url = self.conf["quay"].get("QUAY_URL", "http://localhost")
            stored_manifest = get_mongo_manifest(
                self.conf, self.manifest.id, self.get_url
            )
            if isinstance(stored_manifest, int):
                self.log.info("manifest not found (yet)")
            elif stored_manifest:
                self.log.info("Retrieved manifest %s", stored_manifest.id)
            else:
                self.log.info("Unknown manifest %s", self.manifest.id)

        log.info("Started interface instance %s", self.__class__.__name__)
        self.set_state("started")
        # now = datetime.now().isoformat()
        self.manifest.timestamps.append(datetime.now().isoformat())
        return self

    def __exit__(self, exc_type, exc_value, tb):
        # don't store empty manifests
        if not self.manifest.investigations or not self.manifest.members:
            self.log.warning("Trying to store an empty manifest")
            return
        if exc_type:
            self.log.error("Exception: ", exc_info=(exc_type, exc_value, tb))
            trace = traceback.format_exception(exc_type, exc_value, tb)
            self.manifest.error = Error(message=str(exc_value), details="".join(trace))
            self.set_state("errored")

        self.record()
        log.info("Exiting %s", self)

    def __str__(self):
        n_inv = len(self.manifest.investigations)
        n_stu = len(self.manifest.studies)
        n_ass = len(self.manifest.assays)
        n_img = len(self.manifest.images)
        n_ann = len(self.manifest.quay_annotations)
        return f"""---
         {self.__class__.__name__} managing manifest {self.manifest.id} with

         - {n_inv} investigation{"s" if n_inv > 1 else ""}
         - {n_stu} stud{"ies" if n_stu > 1 else "y"}
         - {n_ass} assay{"s" if n_ass > 1 else ""}
         - {n_img} image{"s" if n_img > 1 else ""}
         - {n_ann} annotation{"s" if n_ann > 1 else ""}

        Current status:  {self.state.status if self.state else "undefined"}
         """

    def record(self):
        if self.has_db:
            if not self.manifest.investigations or not self.manifest.members:
                return

            manifest_json = json_dumper.dumps(self.manifest)
            try:
                manifest_id = post_mongo_manifest(
                    manifest_json, self.conf, self.post_url
                )
                if not manifest_id:
                    self.log.info("Could find manifest in mongo db")
            except Exception as e:
                log.error("Error when trying to post manifest to DB", exc_info=e)
                log.info("DB is not reachable from this clerk")
                self.has_db = False
        else:
            fname = "self.manifest.id.yml"
            store = Path(self.conf.get("YAML_STORE", "/tmp/"))
            if not store.exists():
                store.mkdir(parents=True)
            with (store / fname).open("w") as yh:
                yml = yaml_dumper.dumps(self.manifest)
                yh.write(yml)

    @property
    def isaobjects(self):
        return (
            self.manifest.investigations + self.manifest.studies + self.manifest.assays
        )

    def parse(self):
        raise NotImplementedError

    def get_parent_investigation(self, isaobject):
        if isinstance(isaobject, Investigation):
            return isaobject
        if isinstance(isaobject, Study):
            parent = find_by_id(isaobject.parents[-1], self.manifest.investigations)
        elif isinstance(isaobject, Assay):
            parent = find_by_id(isaobject.parents[-1], self.manifest.studies)
        elif isinstance(isaobject, Image):
            parent = find_by_id(isaobject.parents[-1], self.manifest.assays)
        else:
            msg = f"parent not found for {isaobject.name}"
            raise ValueError(msg)
        return self.get_parent_investigation(parent)


class Clerk(Interface):
    """Abstract manager

    Managers parse a manifest and perform actions on a
    spectific system or between systems
    """

    def __init__(
        self,
        conf: dict,
        manifest: Manifest,
        scheme: str,
        host: str | None = None,
    ):
        """

        required conf entries:

        conf["YAML_STORE"] # Path to store the manifest's yml dumps
        """

        self.created = []
        self.updated = []
        self.deleted = []
        super().__init__(conf=conf, manifest=manifest, scheme=scheme, host=host)

        self.mapping = {}
        self.log.info("Treating manifest with manager %s", self.manager)

    def parse(self):
        """ """
        self.created = []
        self.updated = []
        self.deleted = []
        for assay in self.manifest.assays:
            for importlink in assay.importlinks:
                # this triggers isaobjects imports
                self.log.info(
                    "Importing %s in assay %s", importlink.srce_url, assay.name
                )
            self.register(assay)

        for obj in self.isaobjects:
            if obj.delete:
                self.deleted.append(obj)
                continue
            if self._exists(obj):
                self.updated.append(obj)
            else:
                self.created.append(obj)

        delete_str = "\n\t- ".join([o.name for o in self.deleted])
        create_str = "\n\t- ".join([o.name for o in self.created])
        update_str = "\n\t- ".join([o.name for o in self.updated])

        self.log.info(
            """
    * Objects marked for deletion:
        - %s
    * Objects marked for creation:
        - %s
    * Objects marked for update:
        - %s  """,
            delete_str,
            create_str,
            update_str,
        )

    def crud(self):
        """
        Updates the local hierarchy from the created, updated and deleted
        isaobjects
        """

        if self.state.status == "checked":
            return

        for isaobject in self.created:
            self._create(isaobject)

        for isaobject in self.updated:
            self._update(isaobject)

        for isaobject in self.deleted:
            self._delete(isaobject)

        if self.state.status == "changed":
            self.set_state("checked")
            return
        self.set_state("changed")

    def routine(self, dry=False):
        self.log.info(
            "Started step %i / %i", self.manifest.step + 1, len(self.manifest.route) - 1
        )
        self.log.info("started parse")
        self.parse()
        if not dry:
            self.log.info("finished parse, started crud")
            self.crud()
            self.log.info("finished crud, started transfer")
            self.transfer()
            self.log.info("finished transfer")
            self.log.info("Parse, crud, cleanup again")
            self.parse()
            self.crud()
            self.cleanup()
            self.log.info("finished cleanup")
            for state in self.manifest.states:
                self.log.info("\t %s : %s", state.store, state.status)
                if state.status == "errored":
                    break
                if state.store == self.trgt_store.id:
                    continue
                if state.status in ("checked", "changed"):
                    continue

        self.manifest.step += 1
        self.log.info(
            "Finished step %i / %i", self.manifest.step, len(self.manifest.route) - 1
        )

        if self.manifest.error is not None:
            self.log.error(
                "Got an error in manifest %s: %s",
                self.manifest.id,
                self.manifest.error,
            )
            self.set_state("errored")
        return json_dumper.dumps(self.manifest)

    def cleanup(self):
        pass

    def make_tree_view(self):
        """
        Creates the HTML tree webpage content.
        Uses manifest as source.
        """
        template = jinja_env.get_template("html-tree-view.html.j2")
        return template.render(manifest=self.manifest)

    def _exists(self, isaobject):
        if localobject := self.mapping.get(isaobject.id):
            return localobject
        if localobject := self._find_by_id(isaobject):
            self.mapping[isaobject.id] = localobject
            return localobject
        if localobject := self._find_by_name(isaobject):
            self.mapping[isaobject.id] = localobject
            return localobject
        if localobject := self._find_by_path(isaobject):
            self.mapping[isaobject.id] = localobject
            return localobject
        if localobject := self._find_by_foreign_ids(isaobject):
            self.mapping[isaobject.id] = localobject
            return localobject

        return False

    def _find_by_id(self, isaobject):  # noqa:ARG002
        return False

    def _find_by_name(self, isaobject):  # noqa:ARG002
        return False

    def _find_by_path(self, isaobject):  # noqa:ARG002
        return False

    def _find_by_foreign_ids(self, isaobject):  # noqa:ARG002
        return False

    def _create(self, isaobject):
        raise NotImplementedError

    def _delete(self, isaobject):
        """
        Deletes data
        """
        raise NotImplementedError

    def _update(self, isaobject):
        """
        Updates data based on the manifest
        """
        raise NotImplementedError
