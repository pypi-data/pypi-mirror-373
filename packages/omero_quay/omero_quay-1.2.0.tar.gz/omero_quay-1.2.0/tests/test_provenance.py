from __future__ import annotations

from itertools import product

from omero_quay.core.provenance import get_data_root
from omero_quay.parsers.filesystem import gen_manifest


def test_provenance(data_path):
    provs = ["local", "facility", "docker"]
    for srce, dest in product(provs, provs):
        manifest = gen_manifest(
            data_path / "facility0" / "minimal",
            hierarchy={"investigation": "test", "study": "test", "assay": "test"},
            owner_name="facility0",
            provenance=srce,
            destination=dest,
        )
        assert len([store for store in manifest.route if store]) >= 3
        # first srce_store should not be isa for default route
        srce_store = manifest.route[0]
        assert not srce_store.is_isa


def test_get_data_root(irods_manifest):
    for store in irods_manifest.route:
        if store.id.endswith("Resc"):
            dr = get_data_root(irods_manifest, store.id)
        assert dr
