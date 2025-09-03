"""Connection helpers to LDAP, iRODS, OMERO and madbot"""

from __future__ import annotations

import logging
import urllib

import Ice

log = logging.getLogger()

try:
    from irods.session import iRODSSession
except ImportError:
    log.info(
        """iRODS python client is not installed, if you need it you can install it with
        pip install python-irodsclient"""
    )

try:
    import ezomero
    from omero.cli import CLI
except ImportError:
    log.info("Can't use Omero connection, run pip install omero-quay[server]")
    log.warning("This is only available with administrator privileges on the instance")

try:
    import motor
    import pymongo
except ImportError:
    log.info("Can't use MongDB connection, run pip install omero-quay[server]")
    log.warning(
        "This is only available with administrator privileges on the instance"
        "Users can route GET requests through the tornado server on main quay"
    )


mongo_log = logging.getLogger("pymongo")
mongo_log.setLevel("WARNING")


def mongo_client(conf, is_async=False):
    if is_async:
        return _motor_client(conf)
    return _pymongo_client(conf)


def _mongo_uri(conf):
    mongo_host = conf["mongo"]["DB_HOST"]
    mongo_user = conf["mongo"]["DB_USER"]
    mongo_pass = urllib.parse.quote(conf["mongo"]["DB_PASSWORD"])
    mongo_port = conf["mongo"]["DB_PORT"]
    if conf["mongo"]["DB_USER"] == "root":
        # we're using docker, where the db user is root
        mongo_uri = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}/quay?authSource=admin"
    else:
        mongo_uri = (
            f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}/quay"
        )
    return mongo_uri


def _pymongo_client(conf):
    client = pymongo.MongoClient(_mongo_uri(conf))
    try:
        with pymongo.timeout(3):
            client.server_info()
    except pymongo.errors.PyMongoError as e:
        log.error(
            "Failed to connect to mongo DB with configuration %s",
            conf["mongo"],
            exc_info=e,
        )
        return False
    return client


def _motor_client(conf):
    return motor.motor_tornado.MotorClient(_mongo_uri(conf))


def check_conn(func):
    def wrapped(conf=None, *args, **kwargs):
        try:
            _omero_conn(conf)
            return func(conf, *args, **kwargs)
        except Ice.Exception:
            log.info("No connection with an OMERO server")
            return None

    return wrapped


@check_conn
def omero_conn(conf):
    return _omero_conn(conf)


def _omero_conn(conf):
    """returns a BlitzGateway connection object

    Args:
        conf (json?): output of get_conf() function.
    """

    # https://github.com/ome/omero-cli-transfer/blob/baeb5094430820bf8b0baa499a8faee70e026b09/.omero/wait-on-login

    secure = conf["omero"]["OMERO_HOST"] != "localhost"
    if user := conf["omero"].get("OMERO_ADMIN"):
        log.warning("User user %s with admin privileges", user)
        password = conf["omero"]["OMERO_ADMIN_PASS"]
    elif user := conf["omero"].get("OMERO_USER"):
        password = conf["omero"]["OMERO_USER_PASS"]
    else:
        log.warning("No omero credentials found in config")
        return None

    conn = ezomero.connect(
        user=user,
        password=password,
        host=conf["omero"]["OMERO_HOST"],
        port=conf["omero"]["OMERO_PORT"],
        group=conf["omero"].get("OMERO_GROUP", ""),
        secure=secure,
    )
    if conf["quay"]["is_server"]:
        conn.SERVICE_OPTS.setOmeroGroup(-1)
    conn.c.enableKeepAlive(5)
    return conn


@check_conn
def omero_sudo_conn(conf, username, group=None):
    """returns a BlitzGateway connection object. For sysadmins.

    Args:
        conf (json?): output of get_conf() function.
    """

    # https://github.com/ome/omero-cli-transfer/blob/baeb5094430820bf8b0baa499a8faee70e026b09/.omero/wait-on-login
    secure = conf["omero"]["OMERO_HOST"] != "localhost"
    if user := conf["omero"].get("OMERO_ADMIN"):
        conn = ezomero.connect(
            user=user,
            password=conf["omero"]["OMERO_ADMIN_PASS"],
            host=conf["omero"]["OMERO_HOST"],
            port=conf["omero"]["OMERO_PORT"],
            group=conf["omero"].get("OMERO_GROUP", ""),
            secure=secure,
        )
        conn.SERVICE_OPTS.setOmeroGroup(-1)
        conn.c.enableKeepAlive(5)
        return conn.suConn(username, group)

    conn = ezomero.connect(
        user=conf["omero"]["OMERO_USER"],
        password=conf["omero"]["OMERO_USER_PASS"],
        host=conf["omero"]["OMERO_HOST"],
        port=conf["omero"]["OMERO_PORT"],
        group=conf["omero"].get("OMERO_GROUP", ""),
        secure=secure,
    )
    conn.SERVICE_OPTS.setOmeroGroup(-1)
    conn.c.enableKeepAlive(5)
    return conn


@check_conn
def omero_cli(conf, opts=None):
    if opts is None:
        opts = []
    user = conf["omero"]["OMERO_USER"]
    password = conf["omero"]["OMERO_USER_PASS"]
    host = conf["omero"]["OMERO_HOST"]
    port = conf["omero"]["OMERO_PORT"]
    cli = CLI()

    # FIXME use session key?
    cli.loadplugins()
    args = [
        "login",
        "-w",
        password,
        *opts,
        f"{user}@{host}:{port}",
    ]
    cli.invoke(args, strict=True)
    return cli


@check_conn
def omero_sudo_cli(conf, user, opts=None):
    """Returns an omero CLI instance and connects it
    as the user with the sudo option

    Args:
        conf: output of get_conf() function.
    """
    if opts is None:
        opts = []

    if admin := conf["omero"].get("OMERO_ADMIN"):
        password = conf["omero"]["OMERO_ADMIN_PASS"]
        host = conf["omero"]["OMERO_HOST"]
        port = conf["omero"]["OMERO_PORT"]
        cli = CLI()
        # FIXME use session key?
        cli.loadplugins()
        log.info("sudo login as %s", user)
        args = [
            "login",
            "-w",
            password,
            "--sudo",
            admin,
            *opts,
            f"{user}@{host}:{port}",
        ]
        cli.invoke(args, strict=True)
        return cli

    if user != conf["omero"]["OMERO_USER"]:
        msg = "Not an admin, can't do sudo authentication for another user"
        raise ValueError(msg)
    password = conf["omero"]["OMERO_USER_PASS"]
    host = conf["omero"]["OMERO_HOST"]
    port = conf["omero"]["OMERO_PORT"]
    cli = CLI()
    # FIXME use session key?
    cli.loadplugins()
    log.info("login as %s", user)
    args = ["login", "-w", password, *opts, f"{user}@{host}:{port}"]
    cli.invoke(args, strict=True)
    return cli


def omero_nolog_cli():
    cli = CLI()
    cli.loadplugins()
    # cli.invoke(["logout"])
    return cli


@check_conn
def omero_admin_cli(conf, opts=None):
    """Returns an omero admin CLI instance

    Args:
        conf (yaml file): output of get_conf() function.
    """

    if opts is None:
        opts = []
    admin = conf["omero"]["OMERO_ADMIN"]
    password = conf["omero"]["OMERO_ADMIN_PASS"]
    host = conf["omero"]["OMERO_HOST"]
    port = conf["omero"]["OMERO_PORT"]
    password = conf["omero"]["OMERO_ADMIN_PASS"]
    cli = CLI()
    # cli.conn().SERVICE_OPTS.setOmeroGroup(-1)
    args = ["login", "-w", password, *opts, f"{admin}@{host}:{port}"]
    # FIXME use session key?
    cli.loadplugins()

    cli.invoke(args)
    return cli


def irods_conn(conf):
    """Returns an iRODSSession instance"""
    if admin := conf["irods"].get("IRODS_ADMIN"):
        return iRODSSession(
            host=conf["irods"]["IRODS_HOST"],
            port=conf["irods"]["IRODS_PORT"],
            user=admin,
            zone=conf["irods"]["IRODS_ZONE"],
            password=conf["irods"]["IRODS_ADMIN_PASS"],
        )

    return iRODSSession(
        host=conf["irods"]["IRODS_HOST"],
        port=conf["irods"]["IRODS_PORT"],
        zone=conf["irods"]["IRODS_ZONE"],
        user=conf["irods"]["IRODS_USER"],
        password=conf["irods"]["IRODS_USER_PASS"],
    )


def irods_sudo_conn(conf, username):
    """Returns an iRODSSession instance"""

    if admin := conf["irods"].get("IRODS_ADMIN"):
        return iRODSSession(
            host=conf["irods"]["IRODS_HOST"],
            port=conf["irods"]["IRODS_PORT"],
            zone=conf["irods"]["IRODS_ZONE"],
            user=admin,
            password=conf["irods"]["IRODS_ADMIN_PASS"],
            client_user=username,
        )

    user = conf["irods"]["IRODS_USER"]
    if user != username:
        msg = f"{user} is not admin and can't authentify as user {username}"
        raise ValueError(msg)

    return iRODSSession(
        host=conf["irods"]["IRODS_HOST"],
        port=conf["irods"]["IRODS_PORT"],
        zone=conf["irods"]["IRODS_ZONE"],
        user=conf["irods"]["IRODS_USER"],
        password=conf["irods"]["IRODS_USER_PASS"],
        client_user=username,
    )
