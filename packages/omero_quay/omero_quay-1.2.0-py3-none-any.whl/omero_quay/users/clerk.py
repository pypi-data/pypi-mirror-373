from __future__ import annotations

from linkml_runtime.dumpers import json_dumper

from omero_quay.core.config import get_conf
from omero_quay.core.interface import Clerk
from omero_quay.core.manifest import Investigation, User
from omero_quay.core.utils import get_clerk_class, temp_user


class UserClerk(Clerk):
    """ """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_idp = False
        self.dependents = []

    @property
    def isaobjects(self):
        return self.manifest.members + self.manifest.investigations

    def parse(self):
        for obj in self.isaobjects:
            if obj.delete:
                self.deleted.append(obj)
                continue
            if self._exists(obj):
                self.updated.append(obj)
            else:
                self.created.append(obj)
        self.log.debug(
            "Created: %s, Updated: %s, Deleted: %s",
            self.created,
            self.updated,
            self.deleted,
        )

    def users_from_isa(self):
        members = set()
        for investigation in self.manifest.investigations:
            members = members.union(
                investigation.owners
                + investigation.contributors
                + investigation.collaborators
            )
        return members

    def _delete(self, user):
        """User deletion is in the manifest sense, so the user
        will be removed from the investigation, not deleted form the system (!)
        User existence is outside the perview of omero-quay
        """

    def update_manifest_members(self):
        self.log.info("Resetting and updating manifest members from userclerk")

        self.manifest.members = []
        localmanager = self._exists(temp_user(self.manifest.manager))
        if not localmanager:
            self.log.info("manager not found for manifest")
            return

        for username in self.users_from_isa():
            if user := self._update_from_local(temp_user(username)):
                self.manifest.members.append(user)

    def _update_from_local(self, user):  # noqa:ARG002
        return False

    def set_state(self, status):
        super().set_state(status)
        if self.is_idp:
            for clerk_class in self.dependents:
                with clerk_class(self.conf, self.manifest) as dependent:
                    dependent.set_state(status)

    def routine(self, dry=False):
        if dry:
            return None

        if self.is_idp:
            self.update_manifest_members()

        self.parse()
        self.crud()
        self.cleanup()
        if self.is_idp:
            for clerk_class in self.dependents:
                with clerk_class(self.conf, self.manifest) as dependent:
                    dependent.is_idp = False
                    dependent.routine()

            for state in self.manifest.states:
                self.log.info("\t %s : %s", state.store, state.status)
                if state.status == "errored":
                    break
                if state.store == self.trgt_store.id:
                    continue
                if state.status in ("checked", "changed"):
                    continue

            self.manifest.step += 1
            self.log.info(
                "Finished step %i / %i",
                self.manifest.step,
                len(self.manifest.route) - 1,
            )

        if self.manifest.error is not None:
            self.log.error(
                "Got an error in manifest %s: %s",
                self.manifest.id,
                self.manifest.error,
            )
            self.set_state("errored")
        return json_dumper.dumps(self.manifest)

    def crud(self):
        for obj in self.created:
            if isinstance(obj, User):
                self._create_user(obj)
            elif isinstance(obj, Investigation):
                self._create_investigation(obj)

        for obj in self.updated:
            if isinstance(obj, User):
                self._update_user(obj)
            elif isinstance(obj, Investigation):
                self._update_investigation(obj)

        for obj in self.deleted:
            if isinstance(obj, User):
                self._delete_user(obj)
            elif isinstance(obj, Investigation):
                self._delete_investigation(obj)

    def _create_investigation(self, obj):
        raise NotImplementedError

    def _create_user(self, obj):
        raise NotImplementedError

    def users_from_instance(self):
        raise NotImplementedError

    def _find_by_path(self, isaobject):  # noqa:ARG002
        return False


def from_manifest(manifest, schemes, create_investigations=False):
    """available schemes:
    irods, samba, omero
    """

    for scheme in schemes:
        Clerk_ = get_clerk_class(scheme, "user")

        with Clerk_(get_conf(), manifest, scheme=scheme) as user_clerk:
            user_clerk.log.setLevel("DEBUG")
            user_clerk.log.info("Starting class %s", Clerk_.__class__.__name__)
            user_clerk.parse()
            user_clerk.crud()

        if create_investigations:
            user_clerk.create_investigations()
