"""
TODO : update this

Example of a store declaration:

```python
elpaso_store = Store(
    id="user_elpaso",
    host="elapso",
    resc="elpasoResc",
    data_roots=[
        "irods:///devZone/home/{{ manifest.manager.name }}/mri_crbm/",
        "file:///mnt/SHARE/{{ manifest.manager.name }}",
        "smb:///10.5.0.18/espace_perso",
        "win://Z:/",
    ],
    post_url="http://10.120.20.3",
    scheme="irods",
    is_isa=False,
)
with Path("elpaso_store.json").open("w") as fh:
    json.dump(elpaso_store.model_dump(), fh)
```

elsewhere in the code:

```python
with Path("elpaso_store.json").open("r") as fh:
    elpaso_store = Store(**json.load(fh))
```
"""

from __future__ import annotations

import json
import logging
import platform
import uuid
from pathlib import Path
from urllib.parse import urlparse

from jinja2 import Template

from omero_quay.core.manifest import Provenance, Store
from omero_quay.core.utils import find_by_id

log = logging.getLogger(__name__)


def get_srce_data_root(manifest, *, scheme=None, template=True):
    srce_store = manifest.route[manifest.step].id
    return get_data_root(manifest, srce_store, scheme=scheme, template=template)


def get_trgt_data_root(manifest, *, scheme=None, template=False):
    trgt_store = manifest.route[manifest.step + 1].id
    return get_data_root(manifest, trgt_store, scheme=scheme, template=template)


def get_data_root(manifest, store_id, scheme=None, template=False):
    store = find_by_id(store_id, manifest.route)
    if not store:
        msg = f"Store {store_id} not found"
        raise ValueError(msg)
    if scheme is None:
        scheme = store.scheme
    for root_path in store.data_roots:
        link = urlparse(root_path)
        if link.scheme == scheme:
            return (
                Template(link.path).render(manifest=manifest) if template else link.path
            ).rstrip("/")
    return None


def set_route(manifest, store_ids):
    manifest.route = []
    all_stores = {
        store.id: store
        for store in manifest.provenance.stores + manifest.destination.stores
    }
    route = [all_stores.get(id) for id in store_ids]
    if None in route:
        log.warning(
            "Some stores where not found: %s", set(store_ids).difference(all_stores)
        )
        route = [store for store in route if store]
    manifest.route = route


def set_default_route(manifest):
    manifest.route = []
    if manifest.provenance.route:
        set_route(manifest, manifest.provenance.route)
        return

    srce_user_store = None
    srce_coop_store = None
    srce_omero_store = None
    trgt_omero_store = None
    trgt_coop_store = None

    ingest_stores = {
        store.scheme: store for store in manifest.provenance.stores if not store.is_isa
    }
    if "file" in ingest_stores:
        srce_user_store = ingest_stores["file"]
    else:
        srce_user_store, *_ = ingest_stores.values()

    local_coop_stores = {
        store.scheme: store for store in manifest.provenance.stores if store.is_isa
    }
    if "omero" in local_coop_stores:
        srce_omero_store = local_coop_stores.pop("omero")
    if "file" in local_coop_stores:
        srce_coop_store = local_coop_stores.pop("file")

    for store in manifest.destination.stores:
        if store.scheme == "omero":
            trgt_omero_store = store
        if trgt_coop_store is not None:
            continue
        if store.is_isa and store.scheme in ("irods", "file"):
            trgt_coop_store = store

    route = [
        srce_user_store,
        srce_coop_store,
        srce_omero_store,
        trgt_coop_store,
        trgt_omero_store,
        # update coop after omero import
        trgt_coop_store,
    ]

    set_route(manifest, [store.id for store in route if store is not None])


def get_provenance(conf, name, url=None):
    if name in ("local", "localhost"):
        return get_local_provenance(conf)
    if url is None:
        url = conf["ingest"]["PROVENANCE_URL"]
    link = urlparse(url)
    if link.scheme == "file":
        with (Path(link.path) / f"{name}.json").open("r") as fh:
            return Provenance(**json.load(fh))
    msg = f"Provenance {name}.json not found in {url}"
    raise ValueError(msg)


def get_local_provenance(conf, data_root=None, **kwargs):
    """
    kwargs are passed down to `Provenance(...**kwargs)`

    local provenance comes with three file stores (user, file, omero)

    """

    if data_root is None:
        user_data_root = conf["ingest"].get(
            "DATA_ROOT",
            "/tmp",
        )
        data_root = (Path(user_data_root) / "{{ manifest.manager }}").resolve()
        log.info("Using local data root: %s", data_root)
    local_user_store = get_local_store(
        data_root,
        scheme="file",
        is_isa=False,
        store_id="localUserFile",
    )
    local_coop_store = get_local_store(
        (Path(data_root) / "isa").as_posix(),
        scheme="file",
        is_isa=True,
        store_id="localCoopFile",
    )
    local_omero_store = get_local_store(
        (Path(data_root) / "isa").as_posix(),
        scheme="omero",
        is_isa=True,
        store_id="localOmero",
    )

    return Provenance(
        id=f"{platform.node()}_{uuid.uuid1()}",
        host=platform.node(),
        stores=[local_user_store, local_coop_store, local_omero_store],
        route=[
            local_user_store.id,
            local_coop_store.id,
            local_omero_store.id,
        ],
        **kwargs,
    )


def get_local_store(data_root, *, scheme="file", is_isa=False, store_id=None):
    if not store_id:
        store_id = f"{scheme}{platform.node().capitalize()}"

    return Store(
        id=store_id,
        host=platform.node(),
        data_roots=[
            f"{scheme}://{data_root}",
        ],
        scheme=scheme,
        is_isa=is_isa,
    )
