from __future__ import annotations

import ldap3

from ..core.config import get_conf
from ..core.connect import ldap_conn
from .crud_user import CRUDUser

mapping = {
    "uid": "name",
    "cn": "name",
    "userPassword": "password",
    "givenName": "first_name",
    "sn": "last_name",
    "mail": "email",
    "unix_uid": "uidnumber",
    "unix_gid": "gidnumber",
}


conf = get_conf()["ldap"]
BASEDN = conf["LDAP_ROOT"]


def get_ldap_dict(user):
    """Returns a dictionary suitable for ldap instantiation"""
    return {
        "cn": user.name,
        "gidNumber": user.unix_gid,
        "givenName": user.first_name,
        "homeDirectory": f"/home/{user.name}",
        "loginShell": "/bin/bash",
        "mail": user.email,
        "objectClass": [
            "top",
            "person",
            "posixAccount",
            "shadowAccount",
            "inetOrgPerson",
            "organizationalPerson",
        ],
        "sn": user.last_name,
        "uid": user.name,
        "uidNumber": user.unix_uid,
        "userPassword": user.password,
    }


class LdapUser(CRUDUser):
    def exists(self):
        with ldap_conn(conf) as conn:
            conn.search(
                search_base=BASEDN,
                search_filter=f"(&(objectClass=inetOrgPerson)(uid={self.user.name}))",
                attributes=["*"],
            )
            return conn.response

    def delete(self):
        user_dn = f"uid={self.user.name},{BASEDN}"
        with ldap_conn(conf) as conn:
            conn.delete(user_dn)

    def create(self):
        user_dn = f"uid={self.user.name},{BASEDN}"
        with ldap_conn(conf) as conn:
            conn.add(
                user_dn,
                attributes=get_ldap_dict(self.user),
            )

    def update(self):
        ldap_dict = get_ldap_dict(self.user)
        json_object_formated = {
            k: [(ldap3.MODIFY_REPLACE, v)] for k, v in ldap_dict.items()
        }
        user_dn = f"uid={self.user.name},{BASEDN}"
        with ldap_conn(conf) as conn:
            conn.modify(user_dn, changes=json_object_formated)
