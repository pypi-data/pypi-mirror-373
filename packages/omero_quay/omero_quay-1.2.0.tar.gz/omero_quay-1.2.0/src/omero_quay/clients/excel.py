from __future__ import annotations

import logging

from linkml_runtime.dumpers import json_dumper

from omero_quay.clients.http import post_request
from omero_quay.parsers.excel import parse_xlsx

log = logging.getLogger(__name__)


async def excel_request(xlsx, conf=None, post_url=None):
    """Send a POST request with Excel XLSX content converted to JSON, to iRODS.
    returns nothing.
    """
    manifest = parse_xlsx(xlsx, conf=conf)
    manifest_json = json_dumper.dumps(manifest)
    log.info("Sending manifest : %s from excel", manifest.id)
    return post_request(manifest_json, conf=conf, post_url=post_url)
