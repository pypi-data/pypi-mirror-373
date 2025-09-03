#! /usr/bin/env python
from __future__ import annotations

import asyncio
import logging
import multiprocessing as mp

from omero_quay.core.config import get_conf
from omero_quay.core.http_handler import tornado_server_process
from omero_quay.core.workers import setup

conf = get_conf()

logging.basicConfig(level=logging.ERROR)
log = logging.getLogger("omero_quay")
log.setLevel("DEBUG")


# start the web server in a separate process:
log.info("Starting web handler")
http_handler = mp.Process(target=tornado_server_process)
http_handler.start()

loop = asyncio.new_event_loop()
# print("Running setup")
loop.run_until_complete(setup(conf))
try:
    loop.run_forever()
except KeyboardInterrupt as ki:
    print("Interrupted")  # noqa: T201
    raise ki
