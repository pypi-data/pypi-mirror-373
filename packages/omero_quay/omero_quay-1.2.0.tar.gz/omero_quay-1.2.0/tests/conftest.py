from __future__ import annotations

import asyncio
import time
from pathlib import Path

import pytest

from omero_quay.clients.excel import excel_request
from omero_quay.clients.http import get_mongo_manifest
from omero_quay.core.config import get_conf
from omero_quay.core.connect import irods_sudo_conn
from omero_quay.managers.irods import put_directory
from omero_quay.parsers.filesystem import gen_manifest

pytestmark = pytest.mark.asyncio(scope="module")


@pytest.fixture(scope="session")
def base_import(conf, xlsx_path, irods_user_path):  # noqa:ARG001
    manifest_id = asyncio.run(excel_request(xlsx_path, conf))
    waited = 0
    while waited < 1800:
        time.sleep(30)
        waited += 30
        man = get_mongo_manifest(conf, manifest_id)
        if not man:
            continue
        if msg := man["error"] is not None:
            raise OSError(msg)
        for state in man["states"]:
            if state["status"] == "errored":
                msg = f"Import failed for {state['store']}"
                raise ValueError(msg)
            if (state["store"] == "mesoOmero") and (state["status"] == "checked"):
                return
    raise TimeoutError


@pytest.fixture(scope="session")
def conf():
    return get_conf()


@pytest.fixture(scope="session")
def data_path(conf):
    DATA_PATH = conf["ingest"]["DATA_ROOT"]
    # os.environ["QUAY_TEST_DATA"] = DATA_PATH
    path = Path(DATA_PATH).resolve()
    if not path.exists():
        path.mkdir(parents=True)
    return path


@pytest.fixture(scope="session")
def irods_user_path(data_path, conf):
    test_user = "facility0"
    local_path = data_path / test_user
    logical_path = f"/{conf['irods']['IRODS_ZONE']}/home/"
    # irods_col_path = (Path(logical_path) / local_path.name).as_posix()
    with irods_sudo_conn(conf, test_user) as sess:
        try:
            put_directory(
                local_path=local_path, logical_path=logical_path, session=sess
            )
        except KeyError:
            print("Put directory failed")
        yield logical_path
        # collection = sess.collections.get(irods_col_path)
        # collection.remove(recurse=True, force=True)


@pytest.fixture(scope="session")
def excel_files(data_path):
    return data_path / "excels" / "validation_excels"


@pytest.fixture
def yaml_manifest(data_path):
    return data_path / "manifests" / "base_manifest.yml"


@pytest.fixture
def yaml_manifest_2(data_path):
    return data_path / "manifests" / "base_manifest_2.yml"


@pytest.fixture
def users_manifest(data_path):
    return data_path / "users" / "test_users.yml"


@pytest.fixture
def test_users_json(data_path):
    return data_path / "users" / "test_users.json"


@pytest.fixture(scope="session")
def xlsx_path(data_path):
    return data_path / "excels" / "test_JCB_local.xlsx"


@pytest.fixture
def irods_manifest(irods_user_path):
    source = Path(irods_user_path) / "facility0" / "minimal"
    owner = "facility0"
    return gen_manifest(
        source,
        depth=0,
        hierarchy={
            "investigation": "test_inv",
            "study": "test_stu",
            "assay": "test_ass",
        },
        owner_name=owner,
        scheme="irods",
        provenance="docker",
        destination="docker",
    )


@pytest.fixture
def fs_manifest(data_path):
    source = data_path / "dir0"
    owner = "facility0"
    return gen_manifest(
        source,
        depth=0,
        hierarchy={
            "investigation": "test_inv",
            "study": "test_stu",
            "assay": "test_ass",
        },
        owner_name=owner,
        scheme="file",
        provenance="local",
        destination="docker",
    )
