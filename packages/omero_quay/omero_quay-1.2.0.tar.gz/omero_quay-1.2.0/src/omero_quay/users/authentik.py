from __future__ import annotations

import json
import logging
import os

import requests

from omero_quay.core.config import get_conf
from omero_quay.core.manifest import Manifest, User
from omero_quay.users.clerk import UserClerk
from omero_quay.users.irods import iRODSUserClerk
from omero_quay.users.omero import OmeroUserClerk

log = logging.getLogger(__name__)


MIN_UID = 2000


def get_users(instance):
    conf = get_conf()
    conf["authentik"]["instance"] = instance
    with AuthentikClerk(conf) as clerk:
        return clerk.get_instance_users()
    # manifest = Manifest(id=f"man_{uuid1()}")
    # manifest.members = users
    # return manifest


class AuthentikClerk(UserClerk):
    def __init__(
        self,
        conf: dict,
        manifest: Manifest | None = None,
        host: str | None = None,
    ):
        super().__init__(conf, manifest, scheme="atk", host=host)
        self.is_idp = True
        if self.conf.get("authentik") is None:
            msg = "No authentik section in configuration"
            raise ValueError(msg)

        token = self.conf["authentik"].get("token")
        if not token:
            token = os.environ.get("AUTHENTIK_TOKEN")
        if not token:
            msg = (
                "No authentik token found in your env. var, if you have"
                " sufficient privileges create one and store it in AUTHENTIK_TOKEN"
            )
            raise ValueError(msg)
        self.atk_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        }
        self.atk_url = self.conf["authentik"]["atk_url"]
        instance = self.conf["authentik"]["instance"]
        filter_str = json.dumps({"instance": instance})
        resp = requests.get(
            f"{self.atk_url}/api/v3/core/groups/",
            headers=self.atk_headers,
            params={"attributes": filter_str},
            timeout=10,
        )

        try:
            self.user_group = next(iter(resp.json()["results"]))["name"]
        except StopIteration as e:
            msg = (
                f"Could not determine user group for instance {instance} in authentik "
            )
            raise ValueError(msg) from e

        self.dependents = [OmeroUserClerk, iRODSUserClerk]

    def _exists(self, user):
        resp = requests.get(
            f"{self.atk_url}/api/v3/core/users/",
            headers=self.atk_headers,
            params={"username": user.name, "group": self.user_group},
            timeout=10,
        )
        try:
            return next(iter(resp.json()["results"]))
        except StopIteration:
            return False

    def _update_from_local(self, user):
        atk_user = self._exists(user)
        if not atk_user:
            return None
        return self._translate(atk_user)

    def _translate(self, atk_user):
        attributes = atk_user["attributes"]
        user_id = attributes.get("orcid") if "orcid" in attributes else atk_user["uuid"]
        names = atk_user["name"].split()
        first_name = names[0]
        last_name = " ".join(names[1:]) if len(names) > 1 else ""
        return User(
            id=user_id,
            name=atk_user["username"],
            first_name=first_name,
            last_name=last_name,
            email=atk_user["email"],
        )

    def crud(self):
        """Nothing to do here :)"""

    def get_instance_users(self) -> list[User]:
        # Enter a context with an instance of the API client
        resp = requests.get(
            f"{self.atk_url}/api/v3/core/groups/",
            headers=self.atk_headers,
            params={"name": self.user_group},
            timeout=10,
        )
        try:
            atk_group = next(iter(resp.json()["results"]))
        except StopIteration:
            return False

        atk_users = atk_group["users_obj"]
        return [self._translate(atk_user) for atk_user in atk_users]
