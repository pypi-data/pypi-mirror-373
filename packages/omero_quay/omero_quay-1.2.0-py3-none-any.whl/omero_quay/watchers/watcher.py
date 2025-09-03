"""
Watcher classes or in charge of generating the initial manifest
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from ..core.interface import Interface
from ..core.manifest import Manifest

log = logging.getLogger(__name__)


class Watcher(Interface):
    def __init__(
        self,
        conf: dict,
        scheme: str | None = None,
        host: str | None = None,
    ):
        super().__init__(conf, manifest=None, scheme=scheme, host=host)
        self.clock = datetime.now()
        self.min_delay = conf.get("UPDATE_DELAY", 600)
        log.debug("Watcher delay: %d s", self.min_delay)

    async def watch(self):
        """
        ..code::

        for manifest in watcher.watch():
            manifest_json = json_dumper.dumps(manifest)
            ...
        """
        log.info("%s started watching", self.__class__.__name__)
        while True:
            now = datetime.now().timestamp()
            elapsed = now - self.clock.timestamp()
            wait = max(0, self.min_delay - elapsed)
            log.info("waiting for %s", wait)
            await asyncio.sleep(wait)
            log.info("Watcher looking for past events")
            _clock = datetime.now()
            events = self.find_events()
            self.clock = _clock
            if not events:
                await asyncio.sleep(0.01)
                continue

            if self.gen_manifest(*events) and self.manifest.investigations:
                log.info("%s got non empty manifest", self.__class__.__name__)
                yield self.manifest
                log.info("back in watcher loop")
            else:
                await asyncio.sleep(0.01)

    def find_events(self, since=0):
        raise NotImplementedError

    def gen_manifest(self, *events) -> Manifest:
        raise NotImplementedError
