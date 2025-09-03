from __future__ import annotations

import os
from pathlib import Path

import yaml

from omero_quay.core.config import get_conf, recurse_update


def test_get_default_conf(conf):
    assert "irods" in conf
    assert conf["irods"]["IRODS_PORT"] == 1247


def test_update_conf():
    old_conf = os.environ["QUAY_CONF"]
    update = {"irods": {"IRODS_PORT": 1256}}
    with Path("/tmp/update_conf.yml").open("w", encoding="utf-8") as f:
        yaml.dump(update, f)
    os.environ["QUAY_CONF"] = Path("/tmp/update_conf.yml").resolve().as_posix()
    conf = get_conf()
    assert "omero" in conf
    assert conf["irods"]["IRODS_PORT"] == 1256
    Path("/tmp/update_conf.yml").unlink()
    os.environ["QUAY_CONF"] = old_conf


def test_update_conf_newkey():
    old_conf = os.environ["QUAY_CONF"]
    update = {"new_key": {"new_subkey": "hello"}}
    with Path("/tmp/update_conf.yml").open("w", encoding="utf-8") as f:
        yaml.dump(update, f)
    os.environ["QUAY_CONF"] = Path("/tmp/update_conf.yml").resolve().as_posix()
    conf = get_conf()
    assert "omero" in conf
    assert conf["new_key"]["new_subkey"] == "hello"
    Path("/tmp/update_conf.yml").unlink()
    os.environ["QUAY_CONF"] = old_conf


def test_update_conf_noneval():
    old_conf = get_conf().copy()
    conf = get_conf()
    old_conf["ingest"] = None
    update = recurse_update(old_conf, conf)
    assert update["ingest"] == conf["ingest"]
