"""
Abstract class for manager
"""

from __future__ import annotations

import logging
from collections import defaultdict

from omero_quay.core.interface import Clerk
from omero_quay.core.manifest import Manifest
from omero_quay.core.provenance import set_default_route

log = logging.getLogger(__name__)


class Manager(Clerk):
    """Abstract manager

    Managers parse a manifest and perform actions on a
    spectific system or between systems
    """

    def __init__(
        self,
        conf: dict,
        manifest: Manifest,
        scheme: str,
        host: str | None = None,
    ):
        """

        required conf entries:

        conf["YAML_STORE"] # Path to store the manifest's yml dumps
        """
        super().__init__(conf=conf, manifest=manifest, scheme=scheme, host=host)

        self.mapping = {}
        self.destinations = defaultdict(dict)
        self.log.info("Treating manifest with manager %s", self.manager)
        if not self.manifest.route:
            set_default_route(self.manifest)
        if self.manifest.step is None:
            self.manifest.step = 0

        self.log.info(
            "Step %i / %i: En route from  %s to %s",
            self.manifest.step + 1,
            len(self.manifest.route),
            self.srce_store.id,
            self.trgt_store.id,
        )

    def __exit__(self, exc_type, exc_value, tb):
        super().__exit__(exc_type, exc_value, tb)

    def transfer(self):
        raise NotImplementedError

    def annotate(self):
        raise NotImplementedError

    def package(self):
        raise NotImplementedError

    def register(self, isaobject):
        raise NotImplementedError
