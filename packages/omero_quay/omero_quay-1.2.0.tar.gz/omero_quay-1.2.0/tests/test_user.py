from __future__ import annotations

from omero_quay.core.utils import get_clerk_class, temp_user

json_mapping = {
    "name": "uid",
    "password": "userPassword",
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
    "unix_uid": "uidNumber",
    "unix_gid": "uidNumber",
}


def test_find_by_id(conf, users_manifest):
    for scheme in ("omero",):
        Clerk_ = get_clerk_class(scheme, role="user")
        with Clerk_.from_manifest_yaml(conf, users_manifest) as clerk:
            facility = temp_user("facility0")
            facility.ome_id = 2
            assert clerk._find_by_id(facility)


def test_find_by_name(conf, users_manifest):
    for scheme in ("omero", "irods"):
        Clerk_ = get_clerk_class(scheme, role="user")
        with Clerk_.from_manifest_yaml(conf, users_manifest) as clerk:
            facility = temp_user("facility0")
            facility.ome_id = 2
            assert clerk._find_by_name(facility)


def test_from_manifest(conf, users_manifest):
    for scheme in ("omero", "irods"):
        Clerk_ = get_clerk_class(scheme, role="user")
        with Clerk_.from_manifest_yaml(conf, users_manifest) as clerk1:
            assert clerk1.users_from_isa()
            clerk1.parse()
            clerk1.crud()

    clerk1.manifest.members[0].first_name = "Newname"
    Clerk_ = get_clerk_class("omero", role="user")
    with Clerk_(conf, clerk1.manifest) as clerk2:
        assert clerk2.manifest.members
        user = clerk2.manifest.members[0]
        clerk2.updated.append(user)
        clerk2.crud()
        if scheme == "omero":
            store_user = clerk2._exists(user)
            assert store_user.getFirstName() == "Newname"
