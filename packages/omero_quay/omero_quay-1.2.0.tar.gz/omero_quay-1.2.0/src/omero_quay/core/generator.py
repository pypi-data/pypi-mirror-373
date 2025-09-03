from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid1

from ..core.config import get_conf
from ..core.manifest import (
    Assay,
    DataLink,
    Investigation,
    Manifest,
    State,
    Study,
    srce_url,
)


def gen_manifest(
    owner_name: str,
    hierarchy: dict,
    srce_url: srce_url | None,
    srce_path: str | None,
    depth: int = 0,
    scheme: str = "irods",
) -> Manifest:
    """
    Generate a manifest from a source url or a path.

    The source url is composed of :
    - a `scheme` as "file" or "irods"
    - a root path to the current user's data
    - a relative path pointing to the data create from which to
    generate the manifest

    Parameters
    ----------
    srce_url: string,
    for example:
      file:///home/username/Data/<isa_path>
    or
      htpps://sftp.omero-fbi.tld/username/Data/<isa_path>


    depth 0: assay
    depth 1: study
    depth 2: investigation


    You need to provide investigation, study and assay names in the `hierarchy`
    argument to import data at the assay level. For example:
           hierarchy={"investigation": "test_inv", "study": "test_stu", "assay": "test_ass"}



    """

    if hierarchy is None:
        hierarchy = {}
    conf = get_conf()
    manifest = Manifest(id=f"man_{uuid1()}")
    if srce_path:
        srce_dir = Path(srce_path)
        conf["SRCE_DIR"] = srce_dir.as_posix()
        link = DataLink(
            id=f"lnk_{uuid1()}", owner=owner_name, srce_url=f"{scheme}://{srce_path}"
        )
    elif srce_url:
        link = DataLink(id=f"lnk_{uuid1()}", owner=owner_name, srce_url=srce_url)
    else:
        msg = "Please provide either a srce_path or a srce_url argument"
        raise ValueError(msg)

    match depth:
        case 0:
            if not {"investigation", "study", "assay"}.issubset(hierarchy):
                msg = """
You need to provide investigation, study and assay names in the `hierarchy`
 argument to import data at the assay level. For example:
           hierarchy={"investigation": "test_inv", "study": "test_stu", "assay": "test_ass"}


                        """
                raise ValueError(msg)

            investigation = Investigation(
                id=f"inv_{uuid1()}",
                name=hierarchy["investigation"],
                owner=owner_name,
            )
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
                importlink=link,
            )
            manifest.assays.append(assay)

        case 1:
            if "investigation" not in hierarchy:
                msg = """You need to provide
investigation and study  names in the `hierarchy` argument
to import data at the study level"""
                raise ValueError(msg)

            investigation = Investigation(
                id=f"inv_{uuid1()}",
                name=hierarchy["investigation"],
                owner=owner_name,
            )
            manifest.investigations.append(investigation)
            study = Study(
                id=f"stu_{uuid1()}",
                name=hierarchy["study"],
                owner=owner_name,
                parents=[investigation.id],
                importlink=link,
            )
            manifest.studies.append(study)
        case 2:
            investigation = Investigation(
                id=f"inv_{uuid1()}",
                name=hierarchy["investigation"],
                owner=owner_name,
                importlink=link,
            )
            manifest.investigations.append(investigation)
    now = datetime.now().isoformat()
    state = State(timestamp=now, host="localhost", scheme=scheme, status="started")
    manifest.states = [state]
    return manifest
