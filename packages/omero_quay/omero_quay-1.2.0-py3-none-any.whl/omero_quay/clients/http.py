from __future__ import annotations

import json
import logging

import requests
from linkml_runtime.loaders import json_loader

from omero_quay.core.config import get_conf
from omero_quay.core.manifest import Manifest

log = logging.getLogger(__name__)


def post_request(manifest_json, conf=None, post_url=None):
    """ """
    if conf is None:
        conf = get_conf()
    if post_url is None:
        post_url = f"{conf['quay']['QUAY_URL']}"
        log.info("mongo post url: %s", post_url)
    timeout = conf["ingest"]["timeout"]
    log.info("Posting to tornado")
    resp = requests.post(
        post_url, data=bytes(manifest_json, encoding="utf-8"), timeout=timeout
    )
    if resp.text == 400:
        log.warning("Error 400")
        return 400
    if "Error" in resp.text:
        msg = f"Communication error {resp.text[:100]}"
        raise ValueError(msg)

    manifest_json = resp.text
    manifest = json_loader.loads(resp.text, target_class=Manifest)
    log.info("Post request got manifest: %s", manifest.id)

    return manifest.id


def post_mongo_manifest(manifest_json, conf=None, post_url=None):
    """Send a POST request from a JSON representation, to iRODS.
    returns nothing.
    """
    if conf is None:
        conf = get_conf()
    if post_url is None:
        post_url = f"{conf['quay']['QUAY_URL']}/mongo"
    log.info("mongo post url: %s", post_url)
    timeout = conf["ingest"].get("timeout", 10)
    resp = requests.post(
        post_url, data=bytes(manifest_json, encoding="utf-8"), timeout=timeout
    )
    if resp.text == "400":
        log.warning("Request to post to mongo db  failed")
        return 400
    if resp.status_code != 200:
        log.warning(
            "Request to post to mongo db  failed with code %s", resp.status_code
        )
        return resp.status_code

    manifest_json = resp.text
    manifest = json_loader.loads(resp.text, target_class=Manifest)
    log.info("Mongot request got manifest: %s", manifest.id)

    return manifest.id


default_projection = [
    "investigations",
    "states",
    "timestamps[-1]",
    "error",
    "manager",
]


def get_mongo_manifest(conf, manifest_id, get_url=None):
    timeout = conf["ingest"].get("timeout", 10)
    if get_url is None:
        get_url = conf["quay"].get("QUAY_URL")

    params = {
        "filter": {
            "_id": manifest_id,
        },
        "limit": 1,
    }
    try:
        resp = requests.get(
            f"{get_url}/mongo",
            params={k: json.dumps(v) for k, v in params.items()},
            timeout=timeout,
        )
    except requests.exceptions.ConnectionError as e:
        log.info("no connection to mongodb", exc_info=e)
        return None
    if resp.status_code != 200:
        log.warning("Request to post to mongo db failed with code %s", resp.status_code)
        return resp

    if resp.status_code == 200:
        if len(resp.json()) > 1:
            msg = f"only one manifest should be there, got {len(resp.json)}"
            raise ValueError(msg)
        log.info("Got %d answer(s)", len(resp.json()))
        for m in resp.json():
            if "_id" in m:
                m["id"] = m.pop("_id")
            if "@type" in m:
                m.pop("@type")
            return Manifest(**m)
    log.info(f"Manifest {manifest_id} not Found")
    return None


def get_manifest(conf, manifest_id, get_url=None):
    return get_mongo_manifest(conf, manifest_id, get_url=get_url)
