""" Import data from the configuration listed in an excel file

Sends an http request to     conf["ingest"]["DEST_HOST"]:conf["ingest"]["DEST_PORT"]

"""
from __future__ import annotations

import asyncio
import sys

from omero_quay.clients.excel import excel_request
from omero_quay.core.config import get_conf

if __name__ == "__main__":
    xlsx = sys.argv[1]
    asyncio.run(excel_request(xlsx, conf=get_conf()))
