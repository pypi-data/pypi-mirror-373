from __future__ import annotations

import logging
import os
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid1

import numpy as np
import pandas as pd

from omero_quay.core.config import get_conf
from omero_quay.core.interface import Interface
from omero_quay.core.manifest import (
    Assay,
    DataLink,
    Investigation,
    KVPair,
    MapAnnotation,
    Study,
    TagAnnotation,
)
from omero_quay.core.provenance import (
    get_data_root,
    get_provenance,
    set_default_route,
)
from omero_quay.core.utils import find_by_name

log = logging.getLogger(__name__)


class XlsxParser(Interface):
    def __init__(self, conf, xlsx_path):
        super().__init__(conf=conf, scheme="xlsx", host=os.uname().nodename)
        self.xlsx_path = Path(xlsx_path).resolve()
        self.sheets = {}

    @property
    def srce_store(self):
        for store in self.manifest.provenance.stores:
            if store.scheme == "file":
                return store
        msg = f"{self.manifest.provenance.id} has no file store, can't parse"
        raise ValueError(msg)

    def parse(self):
        self.log.info("Loading excel file %s", self.xlsx_path)
        sheet_names = ["Investigation", "Study", "Assay"]
        sheets = pd.read_excel(self.xlsx_path, sheet_names)
        self.sheets = {
            key: dataframe.dropna(how="all")
            .reset_index(drop=True)
            .replace(pd.NA, "")
            .replace(np.nan, "")
            .apply(_cleanup)
            for key, dataframe in sheets.items()
        }

        # Only one manager is supported
        self.manager = self.sheets["Investigation"].loc[0, "manager"]
        self.manifest.manager = self.manager

        for idx in self.sheets["Investigation"].index:
            self._parse_investigation(idx)

        # Too soon for that !
        # update_manifest_users(self.conf, self.manifest)

        set_default_route(self.manifest)
        # self.manifest.route.insert(0, self.srce_store)
        for idx in self.sheets["Study"].index:
            self._parse_study(idx)
        for idx in self.sheets["Assay"].index:
            self._parse_assay(idx)

        self.set_state("checked")

    def _parse_investigation(self, idx: int):
        row = self.sheets["Investigation"].loc[idx]
        inv = Investigation(
            id=f"inv_{uuid1()}", name=row["name"], description=row["description"]
        )

        inv.owners = row["owners"].split(",")
        inv.contributors = row["contributors"].split(",")
        if inv.contributors and not inv.contributors[0]:
            inv.contributors = []
        inv.collaborators = row["collaborators"].split(",")
        if inv.collaborators and not inv.collaborators[0]:
            inv.collaborators = []

        # self.manifest.members.extend(inv.owners + inv.contributors + inv.collaborators)

        inv.owner = row["owners"].split(",")[0]

        # Now the management is more explicit
        msg = (
            "Provenance not found, make sure the 'provenance' cell "
            "in the Investigation sheet is correct and points to an existing"
            " provenance json file "
        )
        if prov := row.get("provenance"):
            self.manifest.provenance = get_provenance(
                self.conf, prov, self.conf["ingest"]["PROVENANCE_URL"]
            )
            if self.manifest.provenance is None:
                raise ValueError(msg)
        else:
            raise ValueError(msg)

        if dest := row.get("destination"):
            self.manifest.destination = get_provenance(
                self.conf, dest, self.conf["ingest"]["PROVENANCE_URL"]
            )
        else:
            msg = (
                "Destination not found, pleasen make sure the 'destination' cell "
                "in the 'Investigation' sheet is correct"
            )
            raise ValueError(msg)

        self.manifest.investigations.append(inv)

    def _get_srce_url(self, row):
        scheme = self.srce_store.scheme
        root_path = get_data_root(
            self.manifest, self.srce_store.id, scheme=scheme, template=True
        )

        row_path = row["path"].replace("\\", "/")

        if Path(row_path).is_absolute():
            if Path(row_path).is_relative_to(root_path):
                return f"{scheme}://{row_path}"
            msg = f"{row_path} is absolute and not relative to {root_path}, aborting"
            raise ValueError(msg)

        if urlparse(row_path).scheme:
            row_path = Path(urlparse(row_path).path.lstrip("/"))

        return f"{scheme}://{root_path}/{row_path}"

    def _parse_study(self, idx: int):
        stu = self.sheets["Study"].loc[idx]
        inv_name = stu["parent"]
        inv = find_by_name(inv_name, self.manifest.investigations)

        if inv is None:
            msg = f"Parent investigation {inv_name} not found for study {stu['name']}"
            raise KeyError(msg)

        study = Study(
            id=f"stu_{uuid1()}",
            name=stu["name"],
            owner=stu["owner"],
            description=str(stu["description"]),
            parents=[inv.id],
        )
        if stu["tags"] and not pd.isna(stu["tags"]):
            tags = stu["tags"].split(",")
            for tag in tags:
                tag_ann = TagAnnotation(
                    id=f"ann_{uuid1()}",
                    value=tag,
                    namespace="quay",
                )
                self.manifest.quay_annotations.append(tag_ann)
                study.quay_annotations.append(tag_ann.id)

        inv.children.append(study.id)
        self.manifest.studies.append(study)

    def _parse_assay(self, idx: int):
        keys = self.conf["excel"]["keys"]

        ass = self.sheets["Assay"].loc[idx]
        stu_name = ass["parent"]
        study = find_by_name(stu_name, self.manifest.studies)

        if study is None:
            msg = f"Parent study {stu_name} not found for assay {ass['name']}"
            raise KeyError(msg)

        assay = find_by_name(ass["name"], self.manifest.assays)
        if (assay is None) or (study.id not in assay.parents):
            assay = Assay(
                id=f"ass_{uuid1()}",
                name=ass["name"],
                owner=ass["owner"],
                description=str(ass["description"]),
                parents=[study.id],
            )
            study.children.append(assay.id)
            self.manifest.assays.append(assay)

        if ass.get("path"):
            srce_url = self._get_srce_url(ass)
            self.log.info("Found assay import path %s", srce_url)
            assay.importlinks.append(
                DataLink(
                    id=f"imp_{uuid1()}",
                    owner=self.manager,
                    srce_url=srce_url,
                )
            )

        kv_pairs = [KVPair(key=k, value=v) for k, v in dict(ass[keys].dropna()).items()]
        map_ann = MapAnnotation(
            id=f"ann_{uuid1()}", kv_pairs=kv_pairs, namespace="quay"
        )
        assay.quay_annotations.append(map_ann.id)
        self.manifest.quay_annotations.append(map_ann)

        if ass["tags"] and not pd.isna(ass["tags"]):
            tags = ass["tags"].split(",")
            for tag in tags:
                tag_ann = TagAnnotation(
                    id=f"ann_{uuid1()}",
                    value=tag,
                    namespace="quay",
                )
                self.manifest.quay_annotations.append(tag_ann)
                assay.quay_annotations.append(tag_ann.id)


def parse_xlsx(xlsx_path, conf=None):
    xlsx_path = Path(xlsx_path).resolve()
    log.info("Loading excel file %s", xlsx_path)
    if conf is None:
        conf = get_conf()
    with XlsxParser(conf, xlsx_path) as parser:
        parser.parse()
        return parser.manifest


def _cleanup(col):
    quotes = "' «»“”’'"  # noqa:RUF001
    try:
        return col.str.strip(quotes)
    except AttributeError:
        return col


def _parse_samba_path(win_path):
    if ":" in win_path:
        win_path = win_path.split(":")[1]
    win_path = "/".join(win_path.split("\\"))
    return f"smb:/{win_path}"
