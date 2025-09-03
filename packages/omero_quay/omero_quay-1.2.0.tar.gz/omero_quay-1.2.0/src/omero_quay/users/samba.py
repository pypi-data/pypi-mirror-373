from __future__ import annotations

import logging
import subprocess

from omero_quay.core.config import get_conf
from omero_quay.users.clerk import UserClerk

conf = get_conf()
users_home = conf["ingest"]["DATA_ROOT"]

# samba-tool cli arguments
# see `samba-tool user add -h`
mapping: dict = {
    "given-name": "first_name",
    "surname": "last_name",
    "mail-address": "email",
    "uid-number": "unix_uid",
    "gid-number": "unix_gid",
}

log = logging.getLogger(__name__)


class SambaUserClerk(UserClerk):
    def _exists(self, user):
        cmd = ["samba-tool", "user", "show", user.name]
        try:
            results = subprocess.run(cmd, check=True)
            # subprocess.run(["sudo", *cmd], check=True)
        except Exception:
            return False

        for res in results:
            if hasattr(res, "return_code") and res.return_code != 0:
                return False
            if hasattr(res, "returncode") and res.returncode != 0:
                return False

        cmd = [
            "samba-tool",
            "user",
            "show",
            "--attributes=mail",
            user.name,
        ]

        res = subprocess.run(
            cmd,
            capture_output=True,
            check=False,
        )
        try:
            mail = res.stdout.decode("utf-8").split("\n")[1].split(":")[1].strip()
        except IndexError:
            return True

        return mail == self.user.email

    def _delete(self, user):
        cmd = ["samba-tool", "user", "delete", user.name]
        subprocess.run(
            cmd,
            capture_output=True,
            check=True,
        )

    def _create(self, user):
        user_dump = user.model_dump()
        newuser = {k: user_dump[v] for k, v in mapping.items()}
        newuser["home-directory"] = f"/home/{user.name}"

        args = [f"--{k}={v}" for k, v in newuser.items()]
        cmd = [
            "samba-tool",
            "user",
            "add",
            user.name,
            user.name,  # use username as default password
            "--must-change-at-next-login",
            "--use-username-as-cn",
            *args,
        ]

        try:
            subprocess.run(cmd, check=True)
        except Exception as e:
            log.error("Error at user %s creation", user.name, exc_info=e)
            return

    def _update(self, user):  # noqa:ARG002
        log.info("Nothing done, wait for python client implementation")
        # self.delete()
        # self.create()
