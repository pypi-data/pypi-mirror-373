"""
Grab events in omero and feed a worker to update back ISA structure in clients

Thanks a lot to @will-moore for the script
https://github.com/will-moore/python-scripts/blob/e70421e24cc437c8efbcec19729b3c80ef8d4cbb/events.py

https://forum.image.sc/t/is-there-a-way-to-properly-capture-events-in-omero-api/87527
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from uuid import uuid1

import omero
import omero.clients
from ezomero import get_map_annotation_ids
from omero.rtypes import rtime

from omero_quay.core.manifest import Assay, Investigation, Manifest, Study, User
from omero_quay.managers.omero import OmeroManager
from omero_quay.watchers.watcher import Watcher

log = logging.getLogger(__name__)


class OmeroWatcher(Watcher):
    def __init__(
        self,
        conf: dict,
        host: str | None = None,
    ):
        super().__init__(conf, scheme="omero", host=host)
        self._conn = None

        self.manager = self.conf["omero"]["OMERO_ADMIN"]
        self.manifest.manager = self.manager
        self.data_clerk = OmeroManager(conf, self.manifest)

    def __enter__(self):
        super().__enter__()
        self.data_clerk.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)
        self.data_clerk.__exit__(exc_type, exc_value, traceback)

    @property
    def conn(self):
        return self.data_clerk.conn

    def find_events(self, since=0):
        """since: time in seconds before the watcher internal clock.

        The watcher clock can be used in the `watch` method to run every
        conf["omero"]['UPDATE_DELAY'] seconds

        """
        updated_objects = []
        created_objects = []

        self.conn.SERVICE_OPTS.setOmeroGroup(-1)
        query_service = self.conn.getQueryService()

        then = self.clock
        # now = then.replace(hour=then.hour-1)
        log.info("Finding events since: %s", str(then))
        millisecs = (then.timestamp() - since) * 1000

        params = omero.sys.ParametersI()
        offset = 0
        limit = 50
        params.page(offset, limit)

        # params.add("type", rstring("User"))
        params.add("time", rtime(millisecs))

        query = """select e from Event as e
            join fetch e.type as t
            left outer join fetch e.containingEvent as evt
            where t.value=:type and e.time>:time
            order by e.time desc
        """

        results = query_service.findAllByQuery(query, params, None)
        otypes = ("Project", "Dataset", "Image", "Screen", "Plate")
        if not results:
            log.info("No events found")
            return None

        for evt in results:
            log.info(
                "Event id: %s \t @ %s \t event type: %s",
                evt.id.val,
                str(datetime.fromtimestamp(evt.time.val / 1000)),
                evt.type.value.val,
            )
            event_id = evt.id.val
            if self.manager is None:
                ome_user_id = evt.experimenter.id._val
                self.manager = user_from_ome_user(self.conn, ome_user_id)
                self.manager.role = "manager"

            log.info("Event had manager %s", self.manager)
            log.debug("Event details: %s", evt)
            params = omero.sys.ParametersI()
            params.addId(event_id)
            for otype in otypes:
                query = f"select d from {otype} as d where d.details.updateEvent.id=:id"
                obj_ = query_service.findByQuery(query, params, self.conn.SERVICE_OPTS)
                if obj_ is not None:
                    obj = self.conn.getObject(otype, obj_.id.val)
                    updated_objects.append((otype, obj))
                    log.info("Updated %s:%s %s", otype, obj.getId(), obj.getName())
                    continue

                query = (
                    f"select d from {otype} as d where d.details.creationEvent.id=:id"
                )
                obj_ = query_service.findByQuery(query, params, self.conn.SERVICE_OPTS)
                # Get the object weapper not, ProjectI or DatasetI
                if obj_ is not None:
                    obj = self.conn.getObject(otype, obj_.id.val)
                    created_objects.append((otype, obj))
                    log.info("Created %s:%s %s", otype, obj.getId(), obj.getName())

        return created_objects, updated_objects

    def gen_manifest(self, updated_objects, created_objects):
        self.manifest = Manifest(id=f"man_{uuid1()}")
        self.manifest.manager = self.manager.name

        for otype, obj in created_objects + updated_objects:
            log.info("Updated %s:%s from omero", otype, obj.id)
            investigations = {inv.name: inv.id for inv in self.manifest.investigations}
            inv = obj.details.group.name.val
            user = user_from_ome_user(self.conn, obj.getOwner().id)
            user.role = "owner"
            if inv in investigations:
                inv_id = investigations[inv]
            else:
                inv_id = f"inv_{uuid1()}"
                investigation = Investigation(
                    id=inv_id,
                    name=inv,
                    ome_id=obj.details.group.id.val,
                )
                investigation.members.append(self.manager)
                investigation.members.append(user)
                self.manifest.investigations.append(investigation)
                inv_file_path = (
                    Path(self.conf["omero"]["OMERO_SHARE_PATH"]) / investigation.name
                )
                investigation.urls.append(f"file://{inv_file_path}")
                inv_irods_path = (
                    Path(self.conf["omero"]["IRODS_SHARE_PATH"]) / investigation.name
                )
                investigation.urls.append(f"irods://{inv_irods_path}")

            match otype:
                case "Project":
                    study = self._add_study(obj, otype, user, inv_id)

                    self.manifest.studies.append(study)
                    investigation.children.append(study.id)
                    stu_path = Path(investigation.name) / study.name
                    study.urls = [
                        f"file://{self.conf['omero']['OMERO_SHARE_PATH']}/{stu_path}",
                        f"irods://{self.conf['omero']['IRODS_SHARE_PATH']}/{stu_path}",
                    ]

                case "Dataset":
                    for proj in obj.getAncestry():
                        studies = {
                            str(study.name): study.id for inv in self.manifest.studies
                        }
                        if proj.name not in studies:
                            study = self._add_study(proj, otype, user, inv_id)
                            self.manifest.studies.append(study)
                            investigation.children.append(study.id)
                        else:
                            study = studies[proj.name]

                    quay_ids = self._get_quay_ids(obj, otype, user)
                    id_ = quay_ids.get("quay_id")
                    if id_ is None:
                        id_ = f"ass_{uuid1()}"
                    assay = Assay(
                        id=id_,
                        name=obj.name,
                        ome_id=obj.id,
                        irods_id=quay_ids.get("irods_id"),
                        parents=[study.id],
                        owner=user.name,
                    )
                    ass_path = Path(investigation.name) / study.name / assay.name

                    assay.urls = [
                        f"file://{self.conf['omero']['OMERO_SHARE_PATH']}/{ass_path}",
                        f"irods://{self.conf['omero']['IRODS_SHARE_PATH']}/{ass_path}",
                    ]

                    self.manifest.assays.append(assay)
                    study.children.append(assay.id)

        return self.manifest

    def _get_quay_ids(self, obj, otype, user):
        try:
            ann_ids = get_map_annotation_ids(
                self.conn.suConn(user.name), otype, obj.id, ns="quay"
            )
        except AttributeError:
            return {}
        if ann_ids is not None and len(ann_ids):
            ann = self.conn.getObject("MapAnnotation", ann_ids[-1])
            return ann.getMapValueAsMap()
        return {}

    def _add_study(self, obj, otype, user, inv_id):
        quay_ids = self._get_quay_ids(obj, otype, user)
        log.info("Found ids for object %s: %s", obj.name, quay_ids)
        id_ = quay_ids.get("quay_id")
        if id_ is None:
            id_ = f"stu_{uuid1()}"
        # even if it already appeared, we append it (to track multiple changes)
        return Study(
            id=id_,
            name=obj.name,
            ome_id=obj.id,
            irods_id=quay_ids.get("irods_id"),
            parents=[inv_id],
            owner=user.name,
        )


def user_from_ome_user(conn, ome_user_id):
    ome_user = conn.getObject("Experimenter", ome_user_id)

    email = ome_user.getemail()
    if email is None:
        email = "fixme@example.org"

    return User(
        id=str(ome_user.getId()),
        name=str(ome_user.getName()),
        first_name=str(ome_user.getFirstName()),
        last_name=str(ome_user.getLastName()),
        email=email,
    )
