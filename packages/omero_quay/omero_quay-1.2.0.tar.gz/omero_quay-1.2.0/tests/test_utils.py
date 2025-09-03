from __future__ import annotations

from omero_quay.core.manifest import Image
from omero_quay.core.utils import isa_from_isaobject


def test_isa_from_isa_object(fs_manifest):
    inv = fs_manifest.investigations[0]
    i, s, a = isa_from_isaobject(fs_manifest, inv)
    assert i.name == inv.name
    assert (s, a) == (None, None)

    stu = fs_manifest.studies[0]
    i, s, a = isa_from_isaobject(fs_manifest, stu)
    assert i.name == inv.name
    assert s.name == stu.name
    assert a is None

    ass = fs_manifest.assays[0]
    i, s, a = isa_from_isaobject(fs_manifest, ass)
    assert i.name == inv.name
    assert s.name == stu.name
    assert a.name == ass.name

    img = Image(id="test", name="img0.tif", parents=[ass.id])
    fs_manifest.images.append(img)

    i, s, a = isa_from_isaobject(fs_manifest, img)
    assert i.name == inv.name
    assert s.name == stu.name
    assert a.name == ass.name
