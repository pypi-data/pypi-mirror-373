from __future__ import annotations

import re

from ..core.config import get_conf
from ..core.connect import omero_conn
from .errors import (
    ManifestValidationError,
    UserNotInOMEROGroup,
)


def check_if_user_in_group(user_login, group_name):
    """
    Check if OMERO user is in OMERO group. Raise error if not.
    """
    conf = get_conf()
    with omero_conn(conf) as conn:
        group = conn.getObject("ExperimenterGroup", attributes={"name": group_name})
    if not group:
        # New group
        return True

    members = [e._omeName._val for e in group.linkedExperimenterList()]
    if user_login not in members:
        raise UserNotInOMEROGroup(user_login, group_name)

    return True


def validate_manifest(manifest):
    # Validate investigations
    for investigation in manifest.investigations:
        if not investigation.name:
            msg = f"Investigation {investigation.id} has no name"
            raise ManifestValidationError(msg)
        if bool(re.search(r"\s", investigation.name)) is True:
            msg = f"{investigation.name} has spaces and is not a valid name for an investigation"
            raise ManifestValidationError(msg)
        if not investigation.owner:
            msg = f"Investigation {investigation.id} has no valid owner"
            raise ManifestValidationError(msg)
        if investigation.owner not in investigation.owners:
            msg = "Investigation owner not in owners"
            raise ManifestValidationError(msg)
        for child_study_id in investigation.children:  # on garde ce morceau ou pas?
            for study in manifest.studies:
                if (
                    str(child_study_id) == str(study.id)
                    and study.owner != investigation.owner
                ):
                    msg = f"No match between study {study.id} and investigation {investigation.id} owner"
                    raise ManifestValidationError(msg)

    # Validate studies
    for study in manifest.studies:
        if not study.name:
            msg = f"Study {study.id} has no name"
            raise ManifestValidationError(msg)
        if not study.owner:
            msg = f"Study {study.id} has no valid owner"
            raise ManifestValidationError(msg)
        if study.id not in manifest.investigations.children:
            msg = f"Study {study.id} not in valid investigation"
            raise ManifestValidationError(msg)
        for investigation in manifest.investigations:
            if investigation.id not in study.parents:
                msg = f"Study {study.id} does not have valid parents"
                raise ManifestValidationError(msg)
        for child_assay_id in study.children:  # on garde ce morceau ou pas?
            for assay in manifest.assays:
                if str(child_assay_id) == str(assay.id) and assay.owner != study.owner:
                    msg = (
                        f"No match between assay {assay.id} and study {study.id} owner"
                    )
                    raise ManifestValidationError(msg)

    # Validate assays
    for assay in manifest.assays:
        if assay.name == "" or None:
            msg = f"Assay {assay.id} has no name"
            raise ManifestValidationError(msg)
        if assay.owner == "" or None:
            msg = f"Assay {assay.id} has no valid owner"
            raise ManifestValidationError(msg)
        if assay.id not in manifest.studies.children:
            msg = f"Assay {assay.id} not in valid study"
            raise ManifestValidationError(msg)
        for study in manifest.studies:
            if study.id not in assay.parents:
                msg = f"Assay {assay.id} does not have valid parents"
                raise ManifestValidationError(msg)
