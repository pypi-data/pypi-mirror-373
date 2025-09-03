from __future__ import annotations

from pathlib import Path
from uuid import uuid1

from omero_quay.core.config import get_conf
from omero_quay.core.manifest import (
    Assay,
    DataLink,
    Investigation,
    Manifest,
    Study,
    User,
)
from omero_quay.core.provenance import get_provenance, set_default_route


def gen_manifest(
    srce_path,
    depth=0,
    hierarchy=None,
    owner_name=None,
    scheme="file",
    provenance="local",
    destination="docker",
):
    """
    depth 0: assay
    depth 1: study
    depth 2: investigation

    """

    if depth != 0:
        msg = "Import from elswhere than assay is not support"
        raise ValueError(msg)

    if hierarchy is None:
        hierarchy = {}
    conf = get_conf()
    srce_dir = Path(srce_path)
    conf["SRCE_DIR"] = srce_dir.as_posix()
    manifest = Manifest(id=f"man_{uuid1()}")
    link = DataLink(
        id=f"lnk_{uuid1()}", owner=owner_name, srce_url=f"{scheme}://{srce_path}"
    )

    manager = User(
        id=owner_name,
        name=owner_name,
        role="manager",
        first_name=owner_name,
        last_name=owner_name,
        email="test@example.org",
    )
    manifest.members = [manager]
    manifest.manager = manager.name
    manifest.provenance = get_provenance(
        conf, provenance, conf["ingest"]["PROVENANCE_URL"]
    )
    manifest.destination = get_provenance(
        conf, destination, conf["ingest"]["PROVENANCE_URL"]
    )
    set_default_route(manifest)

    if not {"investigation", "study", "assay"}.issubset(hierarchy):
        msg = """
You need to provide investigation, study and assay names in the `hierarchy`
argument to import data at the assay level
                """
        raise ValueError(msg)

    investigation = Investigation(
        id=f"inv_{uuid1()}",
        name=hierarchy["investigation"],
        owner=owner_name,
    )
    investigation.owners = [manager.name]

    manifest.investigations.append(investigation)
    study = Study(
        id=f"stu_{uuid1()}",
        name=hierarchy["study"],
        owner=owner_name,
        parents=[investigation.id],
    )
    manifest.studies.append(study)
    assay = Assay(
        id=f"ass_{uuid1()}",
        name=hierarchy["assay"],
        owner=owner_name,
        parents=[study.id],
        importlinks=[link],
    )
    manifest.assays.append(assay)
    return manifest
