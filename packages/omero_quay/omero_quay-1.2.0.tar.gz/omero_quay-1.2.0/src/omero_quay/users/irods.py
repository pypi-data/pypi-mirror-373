from __future__ import annotations

import logging

from irods.access import iRODSAccess
from irods.exception import (
    CAT_SQL_ERR,
    GroupDoesNotExist,
    NoResultFound,
    UserDoesNotExist,
)

from omero_quay.core.connect import irods_conn, irods_sudo_conn
from omero_quay.core.manifest import Investigation, User
from omero_quay.core.utils import find_by_name, get_identifiers
from omero_quay.users.clerk import UserClerk

log = logging.getLogger(__name__)

mapping = {}


class iRODSUserClerk(UserClerk):
    def __init__(self, conf, manifest):
        self.is_idp = False
        super().__init__(conf, manifest, "irods")

    def _create_user(self, user):
        with irods_conn(self.conf) as sess:
            sess.users.create(user.name, "rodsuser")

    def _create_investigation(self, investigation: Investigation):
        """Creates the iRODS group, sets members"""
        with irods_conn(self.conf) as sess:
            group = self._exists(investigation)
            if not group:
                self.log.info(
                    "Creating investigation group %s in irods", investigation.name
                )
                try:
                    group = sess.groups.create(investigation.name)
                except CAT_SQL_ERR as e:
                    self.log.error("SQL error from irods", exc_info=e)
                irods_members = {}
            else:
                irods_members = {m.name: m for m in group.members}
                owners = set(investigation.owners)
                if common := owners.intersection(irods_members):
                    self.log.info(
                        "The investigation %s already existed,"
                        " and users %s were already members"
                        " we will append studies to it ",
                        investigation.name,
                        common,
                    )
                else:
                    msg = "iRODS group already exists but no owner is a member"
                    raise ValueError(msg)

        zone = self.conf["irods"]["IRODS_ZONE"]
        inv_path = f"/{zone}/home/{investigation.name}"  # TODO parametrize that
        with irods_conn(self.conf) as sess:
            has_coll = sess.collections.exists(inv_path)
            if not has_coll:
                group_coll = sess.collections.create(inv_path)
                self.log.info("Created group collection %s", group_coll)
            else:
                group_coll = sess.collections.get(inv_path)
                self.log.info("Found investigation collection in irods: %s", inv_path)

        self._set_ids_metadata(investigation)
        self._set_access(investigation)
        self.log.info("Investigation %s created", investigation.name)

    def _set_access(self, investigation):
        zone = self.conf["irods"]["IRODS_ZONE"]
        inv_path = f"/{zone}/home/{investigation.name}"  # TODO parametrize that

        with irods_conn(self.conf) as sess:
            group_coll = sess.collections.get(inv_path)
            group = self._exists(investigation)

        irods_members = {m.name: m for m in group.members}
        if self.manager not in irods_members:
            group.addmember(self.manager)
            irods_members = {m.name: m for m in group.members}

        acl = iRODSAccess(
            "delete_object", group_coll, self.manager, user_type="rodsuser"
        )
        acls = [acl]

        acl = iRODSAccess(
            "delete_object",
            group_coll,
            self.conf["irods"]["IRODS_ADMIN"],
            user_type="rodsadmin",
        )
        acls.append(acl)

        for user_id in investigation.owners:
            member = find_by_name(user_id, self.manifest.members)
            if member is None:
                msg = "Maybe you don't have access to member information"
                self.log.warning(msg)
                continue

            if member.name not in irods_members:
                group.addmember(member.name)
                irods_members = {m.name: m for m in group.members}
                self.log.info("Adding %s as owner of %s", member.name, group_coll)
            acl = iRODSAccess("own", group_coll, member.name, user_type="rodsuser")
            acls.append(acl)

        for user_id in investigation.contributors:
            member = find_by_name(user_id, self.manifest.members)
            if member.name not in irods_members:
                group.addmember(member.name)
                irods_members = {m.name: m for m in group.members}
                self.log.info("Adding %s as contributor of %s", member.name, group_coll)
            acl = iRODSAccess("write", group_coll, member.name, user_type="rodsuser")
            acls.append(acl)

        for user_id in investigation.collaborators:
            member = find_by_name(user_id, self.manifest.members)
            if member.name not in irods_members:
                group.addmember(member.name)
                irods_members = {m.name: m for m in group.members}
                self.log.info(
                    "Adding %s as collaborator of %s", member.name, group_coll
                )
            acl = iRODSAccess("read", group_coll, member.name, user_type="rodsuser")
            acls.append(acl)

        inh_acl = iRODSAccess("inherit", group_coll)
        with irods_sudo_conn(self.conf, self.manager) as sess:
            self.log.info("Set inherit for %s", group_coll)
            sess.acls.set(inh_acl)
            for acl in acls:
                sess.acls.set(acl)

        with irods_conn(self.conf) as sess:
            group = sess.groups.get(investigation.name)

        admin = self.conf["irods"]["IRODS_ADMIN"]
        if admin not in {m.name for m in group.members}:
            group.addmember(admin)
        admin_acl = iRODSAccess(
            "delete_object", group_coll, admin, user_type="rodsadmin"
        )

        with irods_sudo_conn(self.conf, self.manager) as sess:
            self.log.info("Setting admin as group owner")
            sess.acls.set(admin_acl)

    def _set_ids_metadata(self, investigation):
        with irods_conn(self.conf) as sess:
            group = sess.groups.get(investigation.name)
            self.log.info("Updating irods id %i for %s", group.id, investigation.name)

            investigation.irods_id = group.id
            for key, val in get_identifiers(investigation).items():
                if key in group.metadata.keys():  # noqa:SIM118
                    old = group.metadata.get_all(key)[-1]
                    self.log.debug("old: %s, new: %s", str(old.value), str(val))
                    if str(old.value) != str(val):
                        self.log.info(
                            "Updating %s for object %s", key, investigation.name
                        )
                        group.metadata.set(key, str(val))
                else:
                    self.log.info("Setting %s for object %s", key, investigation.name)
                    group.metadata.add(key, str(val))

    def update_manifest_members(self):
        """Not this clerk's role"""

    def _find_by_name(self, isaobject):
        with irods_conn(self.conf) as sess:
            if isinstance(isaobject, User):
                try:
                    return sess.users.get(isaobject.name)
                except UserDoesNotExist:
                    return False
            if isinstance(isaobject, Investigation):
                try:
                    return sess.groups.get(isaobject.name)
                except (GroupDoesNotExist, NoResultFound):
                    return False
        return False

    def _delete_user(self, user):
        with irods_conn(self.conf) as sess:
            sess.users.remove(user.name)

    def _delete_investigation(self, inv):
        with irods_conn(self.conf) as sess:
            sess.groups.remove(inv)

    def _update_investigation(self, investigation):
        self._set_ids_metadata(investigation)
        self._set_access(investigation)

    def _update_user(self, user):
        """No need to update users in iRODS"""
