from __future__ import annotations

import click
from linkml_runtime.dumpers import yaml_dumper

from omero_quay.core.manifest import User
from omero_quay.users.irods import iRODSUser
from omero_quay.users.ldap import LdapUser
from omero_quay.users.samba import SambaUser


@click.command()
@click.option("--ldap", help="Create in LDAP", is_flag=True)
@click.option("--irods", help="Create in iRODS", is_flag=True)
@click.option("--samba", help="Create in SAMBA", is_flag=True)
def create(ldap=True, irods=True, samba=False):
    if not any((ldap, samba, irods)):
        click.echo("choose at least one option among --ldap --irods --samba")
        return

    login = click.prompt("login", type=str)
    email = click.prompt("email", type=str)
    first_name = click.prompt("first name", type=str)
    last_name = click.prompt("last name", type=str)
    password = click.prompt(
        "password", type=str, hide_input=True, confirmation_prompt=True
    )
    uid = click.prompt("Unix uid", type=int)

    user = User(
        id=login,
        name=login,
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=password,
        unix_uid=uid,
        unix_gid=uid,
    )

    classes = []
    if ldap:
        classes.append(LdapUser)
    if samba:
        classes.append(SambaUser)
    if irods:
        classes.append(iRODSUser)

    for kls in classes:
        kls(user=user).crud()

    click.echo(f"user {user.name} created")
    click.echo(yaml_dumper.dumps(user))


if __name__ == "__main__":
    create()
