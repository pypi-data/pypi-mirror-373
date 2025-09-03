from __future__ import annotations

import json
import logging
from dataclasses import dataclass

from ..core.manifest import User

log = logging.getLogger(__name__)


@dataclass
class CRUDUser:
    user: User

    @classmethod
    def from_dict(cls, users_dict: dict, mapping: dict | None = None) -> CRUDUser:
        if mapping:
            mapped = {k: users_dict.get(v) for k, v in mapping.items()}
            user = User(id=mapped["name"], **mapped)
        else:
            user = User(id=users_dict["name"], **users_dict)
        return cls(user)

    @classmethod
    def from_json(cls, user_json: str, json_mapping: dict | None = None) -> CRUDUser:
        """Creates a user from a json string (such as the one sent by our identity provider)"""
        json_dict = json.loads(user_json)
        return cls.from_dict(json_dict, mapping=json_mapping)

    def crud(self):
        if self.user.delete:
            log.info("%s deletes %s", self.__class__.__name__, self.user.name)
            self.delete()
            return
        if not self.exists():
            log.info("%s creates %s", self.__class__.__name__, self.user.name)
            self.create()
        else:
            log.info("%s updates %s", self.__class__.__name__, self.user.name)
            self.update()

    def exists(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def create(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError
