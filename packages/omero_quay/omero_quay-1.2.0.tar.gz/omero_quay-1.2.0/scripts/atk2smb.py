from __future__ import annotations

import argparse

from omero_quay.users.authentik import get_users


def get_args():
    parser = argparse.ArgumentParser(
        prog="atk2smb",
        description="""Command line interface to create users the facility SAMBA from authentik.

                    The environment variable AUTHENTIK_TOKEN should be set with a valid token
                    or such token should be set in conf['authentik']['token']
                    """,
    )
    parser.add_argument(
        "instance",
        help="Instance from which we select users, e.g. Nantes or Montpellier",
    )  # positional argument
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    users = get_users(args.instance)
