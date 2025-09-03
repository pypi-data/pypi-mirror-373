"""
Copyright (c) 2025 France BioImaging All rights reserved.

omero-quay: Omero Data Import Export Queue

Async logging code from

https://www.zopatista.com/python/2019/05/11/asyncio-logging/
thanks to them !

"""

from __future__ import annotations

import asyncio
import logging
import os
from logging.handlers import QueueListener
from pathlib import Path
from queue import SimpleQueue as Queue

srce_path = Path(__file__).parent.parent.parent
test_path = srce_path / "tests"


# Async log needs a queue handler to not be blocking


class LocalQueueHandler(logging.handlers.QueueHandler):
    def emit(self, record: logging.LogRecord) -> None:
        # Removed the call to self.prepare(), handle task cancellation
        try:
            self.enqueue(record)
        except asyncio.CancelledError:
            raise
        except Exception:
            self.handleError(record)


HOME = Path(os.environ["HOME"])


log_path = HOME / "log" / "omero_quay"
log_path.mkdir(parents=True, exist_ok=True)
log_file = log_path / "main.log"

queue = Queue()
handler = LocalQueueHandler(queue)

log = logging.getLogger("omero_quay")
log.addHandler(handler)

file_handler = logging.FileHandler(log_file.as_posix())

listener = QueueListener(queue, file_handler, respect_handler_level=True)
listener.start()
