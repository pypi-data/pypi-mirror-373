#!/usr/bin/env python
#
# Copyright (c) 2024 FBI.data.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path

import requests
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import render
from omeroweb.decorators import login_required
from pydantic import ValidationError

from omero_quay.clients.excel import excel_request
from omero_quay.core.config import get_conf
from omero_quay.core.manifest import Manifest
from omero_quay.parsers import validate_excel
from omero_quay.parsers.errors import ExcelValidationError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


BASE_DIR = Path(__file__).parent.resolve()
# unix only
HOME = Path(os.environ["HOME"])


syslog_handler = logging.handlers.SysLogHandler()
syslog_handler.setLevel("DEBUG")
logger.addHandler(syslog_handler)


# /tmp/omero_import_webui_files/log_files
quay_path = HOME / "quay-import"
log_path = quay_path / "logs"

log_path.mkdir(parents=True, exist_ok=True)

filelog_handler = logging.FileHandler(log_path / "main.log")
filelog_handler.setLevel("DEBUG")
logger.addHandler(filelog_handler)

# os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logger.info("WebImportUI module imported")

users_files_path = quay_path / "user_excel_files"
users_files_path.mkdir(parents=True, exist_ok=True)

log_files_path = log_path


def import_to_meso(xlsx_file):
    """
    Send a XLSX file to mesocenter, to be processed by omero-quay on mesocenter

    Args:
        xlsx_file: XLSX metadata file. Must be valid.
    """
    config_data = get_conf()
    asyncio.run(excel_request(xlsx_file, config_data))


# login_required: if not logged-in, will redirect to webclient
# login page. Then back to here, passing in the 'conn' connection
# and other arguments **kwargs.
@login_required()
def index(request, conn=None, **kwargs):
    """
    Main Django app function. Returns a Django request.

    Args:
        request: Django request. Mandatory.
        conn: OMERO connection. See OMERO doc for that.
    """
    logger.info("Logging works!")
    # We can load data from OMERO via Blitz Gateway connection.
    # See https://docs.openmicroscopy.org/latest/omero/developers/Python.html
    # A dictionary of data to pass to the html template
    experimenter = conn.getUser()
    context = {
        "firstName": experimenter.firstName,
        "lastName": experimenter.lastName,
        "experimenterId": experimenter.id,
        "loaded_file": "",
        "manifests": [],
    }

    messages.debug(
        request,
        f"Logged in as {experimenter.firstName} {experimenter.lastName}",
    )

    context.update(kwargs)
    user_directory_name = "{firstName}_{lastName}_{experimenterId}".format(**context)
    user_path = quay_path / user_directory_name
    user_path.mkdir(parents=True, exist_ok=True)

    config_data = get_conf()

    http_proxy = os.environ.get("HTTP_PROXY", None)
    # env var might exist but be an empty string
    if not http_proxy:
        http_proxy = None
    logger.info("Proxy: %s", http_proxy)
    params = {
        "filter": {"manager": experimenter.omeName},
        "limit": 200,
        "projection": [
            "investigations",
            "states",
            "timestamps",
            "error",
            "manager",
        ],
    }

    req = requests.get(
        config_data["quay"]["QUAY_URL"],
        params={k: json.dumps(v) for k, v in params.items()},
        timeout=10,
    )
    if req.status_code == 200:
        logger.info("Got %d answers", len(req.json()))
        for i, m in enumerate(req.json()):
            m["id"] = m.pop("_id")
            try:
                manifest = Manifest(**m)
            except ValidationError:
                logger.info("invalid or outdated manifest")
                continue

            logger.info("Loaded manifest %s", m["id"])
            context["manifests"].append(m)
            if manifest.error is not None and i == 0:
                messages.error(request, manifest.error.message)
    else:
        logger.info("tornado GET failed with status: %d", req.status_code)
        messages.error(request, "Could not contact mongodb.")

    fs = FileSystemStorage(location=user_path.as_posix())

    if "import_from_excel" in request.POST and request.method == "POST":
        logger.info("POST_REQUEST: %s", list(request.POST.items()))
        logger.info("request.FILES: %s", list(request.FILES.items()))
        if myfile := request.FILES.get("myfile"):
            filename = fs.save(myfile.name, myfile)
            context["loaded_file"] = filename
            logger.info("importing from %s", filename)
        else:
            return render(request, "quay_import/index.html", context)

        filepath = user_path / filename
        try:
            validate_excel.check_everything(filepath)
            asyncio.run(excel_request(filepath, config_data))
            fs.delete(filename)
            state_string = f"{filename}: Import démarré"
            messages.success(request, state_string)
        except ExcelValidationError as e:
            state_string = f"Erreur de validation pour {filename}: {e}"
            logger.info(state_string)
            messages.error(request, state_string)
        finally:
            for p in user_path.iterdir():
                p.unlink()
        return HttpResponseRedirect(request.path)
        # return render(request, "quay_import/index.html", context)

    return render(request, "quay_import/index.html", context)
