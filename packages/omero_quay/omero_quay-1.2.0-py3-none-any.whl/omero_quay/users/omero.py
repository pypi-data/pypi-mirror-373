from __future__ import annotations

import logging

from omero.rtypes import rstring

from omero_quay.core.connect import omero_admin_cli, omero_conn
from omero_quay.core.manifest import Investigation, User
from omero_quay.core.utils import find_by_name, get_class_mappings
from omero_quay.users.clerk import UserClerk
from omero_quay.users.irods import iRODSUserClerk

log = logging.getLogger(__name__)


class OmeroUserClerk(UserClerk):
    def __init__(self, conf, manifest):
        super().__init__(conf, manifest, "omero")
        self._type_mapping = get_class_mappings("ome")
        self.is_idp = self.conf["omero"].get("IS_IDP", False)
        if self.is_idp:
            self.dependents = [iRODSUserClerk]

    def type_mapping(self, isaobject):
        return self._type_mapping[isaobject.__class__.__name__]

    def _fetch(self, user, conn):
        omero_user = False
        users = conn.getObjects(
            "Experimenter",
            attributes={"omeName": user.name},
        )
        try:
            omero_user = next(iter(users))
        except StopIteration:
            omero_user = False
        return omero_user

    def _find_by_id(self, isaobject):
        otype = self.type_mapping(isaobject)
        if isaobject.ome_id is not None:
            with omero_conn(self.conf) as conn:
                obj = conn.getObject(otype, isaobject.ome_id)
                if obj:
                    self.log.debug("Found object %s by id", isaobject.name)
                    return obj
        return False

    def _find_by_foreign_ids(self, isaobject):  # noqa:ARG002
        """Research by foreign id is not implemented"""
        return False

    def _find_by_name(self, isaobject):
        if isinstance(isaobject, Investigation):
            with omero_conn(self.conf) as conn:
                self.log.debug("Contacting OMERO to find by name")
                groups = conn.getObjects(
                    "experimentergroup", attributes={"name": isaobject.name}
                )

                try:
                    next(iter(groups))
                except StopIteration:
                    return False

            # search for investigation in owners' groups
            for owner in isaobject.owners:
                with omero_conn(self.conf) as conn:
                    (ome_user,) = conn.getObjects(
                        "experimenter", attributes={"omeName": owner}
                    )
                    grps = {p.name: p for p in ome_user.listParents()}

                    if isaobject.name in grps:
                        self.log.info(
                            "Investigation %s already exists in omero and %s is among owners",
                            isaobject.name,
                            owner,
                        )
                        return grps[isaobject.name]
            log.warning(
                "Investigation %s already exists in omero but no one from it's owners is a member",
                isaobject.name,
            )

        elif isinstance(isaobject, User):
            with omero_conn(self.conf) as conn:
                return self._fetch(isaobject, conn)

        return False

    def _update_investigation(self, investigation):
        localobject = self._exists(investigation)
        if not localobject:
            self.log.info(
                "Object %s of type  %s has no mapping in omero",
                investigation.name,
                type(investigation),
            )
            return
        omero_id = localobject.getId()
        investigation.ome_id = omero_id

    def _update_from_local(self, user):
        omero_user = self._exists(user)

        if not omero_user:
            return None
        # For non admin users, querying antother user
        # returns an empty email
        if hasattr(omero_user, "email") and omero_user.email:
            email = omero_user.email
        else:
            self.log.warning("Could not find email in OMERO")
            email = "empty@example.org"

        return User(
            id=user.id,
            name=omero_user.omeName,
            first_name=omero_user.firstName,
            last_name=omero_user.lastName,
            email=email,
        )

    def update_manifest_members(self):
        if not self.conf["omero"].get("OMERO_ADMIN"):
            log.warning("Can't update other users from here, no sufficient rights")
            return
        super().update_manifest_members()

    def _delete_investigation(self, investigation):
        cli = omero_admin_cli(self.conf)
        log.info("Removing everyone from group %s", investigation.name)
        for user in self.users_from_isa():
            cli.invoke(
                [
                    "group",
                    "removeuser",
                    "--user-name",
                    user,
                    "--name",
                    investigation.name,
                ]
            )

    def _delete_user(self, user):
        cli = omero_admin_cli(self.conf)
        log.info("Deactivating user %s in omero", user.name)
        cli.invoke(
            [
                "user",
                "leavegroup",
                "user",
                f"--name={user.name}",
            ]
        )

    def _create_investigation(self, investigation):
        # https://omero.readthedocs.io/en/stable/sysadmins/cli/usergroup.html
        # self.update_manifest_members()
        user_name = self.manager
        user = find_by_name(user_name, self.manifest.members)
        with omero_conn(self.conf) as conn:
            if not self._exists(user):
                self.log.info("Creating user %s in omero", user.name)
                self._create_user(user)

            (ome_user,) = conn.getObjects(
                "experimenter", attributes={"omeName": user_name}
            )

            # set read_annotate permission
            group_id = conn.createGroup(
                name=investigation.name, owner_Ids=[ome_user.id], perms="rwra--"
            )

            investigation.ome_id = group_id
            group = conn.getObject("ExperimenterGroup", group_id)
            self.mapping[investigation.id] = group
            self._update_members(investigation, group)

    def _update_members(self, investigation, group):
        self.log.info("Updating members from omeromanager")

        cli = omero_admin_cli(self.conf)

        owners = [
            self.conf["omero"]["OMERO_ADMIN"],
            self.manifest.manager,
            *investigation.owners,
        ]

        for owner in owners:
            cli.invoke(
                [
                    "group",
                    "adduser",
                    "--name",
                    investigation.name,
                    "--as-owner",
                    owner,
                ],
                strict=True,
            )

        for member in investigation.contributors + investigation.collaborators:
            cli.invoke(
                [
                    "group",
                    "adduser",
                    "--name",
                    investigation.name,
                    member,
                ],
                strict=True,
            )

        cli.invoke(
            [
                "group",
                "removeuser",
                "--name",
                investigation.name,
                "--as-owner",
                self.conf["omero"]["OMERO_ADMIN"],
            ],
            strict=True,
        )
        self.mapping[investigation.id] = group

    def _create_user(self, user):
        cli = omero_admin_cli(self.conf)
        if self._exists(user):
            self.log.info("User %s exists", user.name)
            return

        self.log.info("Creating user %s in omero", user.name)

        if user.email and self.is_idp:
            self.log.warning("!!! Creating user in omero with default password !!!")
            cli.invoke(
                [
                    "user",
                    "add",
                    "-P",
                    "omero",
                    "-e",
                    user.email,
                    user.name,
                    user.first_name,
                    user.last_name,
                    "user",
                ],
                strict=False,
            )
        elif self.is_idp:
            self.log.warning("!!! Creating user in omero with default password !!!")
            cli.invoke(
                [
                    "user",
                    "add",
                    "-P",
                    "omero",
                    user.name,
                    user.first_name,
                    user.last_name,
                    "user",
                ],
                strict=False,
            )
        else:
            self.log.info("Declared LDAP user in omero")
            cli.invoke(
                [
                    "ldap",
                    "create",
                    user.name,
                ],
                strict=False,
            )

        localuser = self._exists(user)
        user.ome_id = localuser.getId()

    def _update_user(self, user):
        with omero_conn(self.conf) as conn:
            conn.SERVICE_OPTS.setOmeroGroup(0)
            conn.getUpdateService()
            omero_user = self._fetch(user, conn)
            omero_user.setOmeName(rstring(user.name))
            omero_user.setFirstName(rstring(user.first_name))
            omero_user.setLastName(rstring(user.last_name))
            if user.email:
                omero_user.setEmail(rstring(user.email))
            omero_user.save()
