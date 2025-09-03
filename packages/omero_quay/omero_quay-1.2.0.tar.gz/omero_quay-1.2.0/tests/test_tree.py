from __future__ import annotations

from omero_quay.core.config import get_conf
from omero_quay.core.interface import Clerk


def test_make_tree(fs_manifest):
    conf = get_conf()
    dumb_clerk = Clerk(conf, fs_manifest, scheme="file")
    tree_html = dumb_clerk.make_tree_view()
    assert fs_manifest.id in tree_html
