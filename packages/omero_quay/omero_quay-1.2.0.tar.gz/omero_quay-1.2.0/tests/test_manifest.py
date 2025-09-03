from __future__ import annotations

from linkml_runtime.loaders import yaml_loader

import omero_quay.core.manifest as mn


def test_load_yml(yaml_manifest):
    manifest = yaml_loader.loads(yaml_manifest.as_posix(), target_class=mn.Manifest)
    assert manifest.investigations
    assert manifest.studies
