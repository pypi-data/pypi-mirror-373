from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import click
from irods.session import iRODSSession

from omero_quay.clients.excel import excel_request
from omero_quay.core.config import get_conf
from omero_quay.managers.irods import put_directory

log = logging.getLogger("omero-quay")
log.setLevel("DEBUG")

SSL_options = {
    "irods_client_server_policy": "CS_NEG_REQUIRE",
    "irods_client_server_negotiation": "request_server_negotiation",
    "irods_ssl_verify_server": "none",
    "irods_encryption_key_size": 16,
    "irods_encryption_salt_size": 8,
    "irods_encryption_num_hash_rounds": 16,
    "irods_encryption_algorithm": "AES-256-CBC",
}


@click.command()
@click.argument("excel_file")
@click.argument("irods_dest")
def main(excel_file, irods_dest):
    login = click.prompt("login", type=str)
    password = click.prompt("password", type=str, hide_input=True)

    local_path = Path(excel_file).resolve().parent
    conf = get_conf()
    log.info(conf["irods"])

    zone = conf["irods"]["IRODS_ZONE"]
    if not Path(irods_dest).is_absolute():
        logical_path = (
            (Path(f"/{zone}") / "home" / login / irods_dest).resolve().as_posix()
        )
    else:
        logical_path = irods_dest
    with iRODSSession(
        host=conf["irods"]["IRODS_HOST"],
        port=conf["irods"]["IRODS_PORT"],
        user=login,
        password=password,
        irods_zone_name=conf["irods"]["IRODS_ZONE"],
        authentication_scheme="pam_password",
        **SSL_options,
    ) as session:
        log.info("Copying %s to %s", local_path, logical_path)
        put_directory(
            local_path,
            logical_path,
            session,
        )

    asyncio.run(excel_request(excel_file))


if __name__ == "__main__":
    main()
