from __future__ import annotations

import logging
import os
from pathlib import Path

import yaml

log = logging.getLogger(__name__)

this_dir = Path(__file__).parent

default_path = (Path(__file__).parent / "quay.yml").resolve()

config_file_paths = [
    Path("/etc/quay/quay.yml"),
    Path(os.environ["HOME"]) / ".config" / "quay.yml",
    Path("quay.yml"),
    default_path,
]


def get_conf():
    """Returns a configuration dictionary

    Defaults are grabbed from (first found first used):
    - /etc/quay/quay.yml
    - $HOME/.config/quay.yml
    - the quay.yml file in the interpreter's working directory
    - the quay.yml file in omero-quay source

    If the environment variable  `QUAY_CONF` is defined and points
    to a valid yml file, this one is used to update the defaults
    """
    with default_path.open("r", encoding="utf-8") as f:
        log.info("Using defaults from %s", default_path.resolve().as_posix())
        defaults = yaml.safe_load(f)

    conf_file = os.environ.get("QUAY_CONF")
    if conf_file is None:
        for conf_file in config_file_paths:
            if not conf_file.exists():
                continue
            break
    else:
        conf_file = Path(conf_file)

    with conf_file.open("r", encoding="utf-8") as f:
        log.info("Using configuration from %s", conf_file.resolve().as_posix())
        new_conf = yaml.safe_load(f)

    return recurse_update(defaults, new_conf)


def recurse_update(old_nested_dict, new_nested_dict):
    """Update recursively the content of nested dictionary plain files."""
    if old_nested_dict is None:  # empty dict in yaml
        old_nested_dict = {}
    for key, val in new_nested_dict.items():
        if val and isinstance(val, dict) and (key in old_nested_dict):
            old_nested_dict[key] = recurse_update(old_nested_dict[key], val)
        else:
            old_nested_dict[key] = val
    return old_nested_dict
