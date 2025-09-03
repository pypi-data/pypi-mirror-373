from __future__ import annotations

import asyncio
import json
import logging

import zmq
import zmq.asyncio
from linkml_runtime.dumpers import json_dumper
from linkml_runtime.loaders import json_loader
from pydantic import ValidationError
from zmq.asyncio import Context

from omero_quay.core.http_handler import repost
from omero_quay.core.manifest import Manifest
from omero_quay.managers.filesystem import FSManager
from omero_quay.managers.irods import iRODSManager
from omero_quay.managers.omero import OmeroManager
from omero_quay.managers.rocrate import RoCrateManager
from omero_quay.mdp.client import Client
from omero_quay.mdp.scheduler import Scheduler
from omero_quay.mdp.worker import Worker
from omero_quay.users.authentik import AuthentikClerk
from omero_quay.users.omero import OmeroUserClerk

# from omero_quay.watchers.omero import OmeroWatcher


NUM_DISPATCH = 2  # Number of possible parallel imports
NUM_WORKERS = 2


log = logging.getLogger(__name__)


def init_event_loop():
    loop = zmq.asyncio.ZMQEventLoop()
    asyncio.set_event_loop(loop)
    return loop


async def dispatch():
    ctx = Context.instance()
    router = ctx.socket(zmq.ROUTER)
    router.setsockopt(zmq.IDENTITY, b"dispatch")
    router.bind(f"tcp://*:{5556}")

    message = await router.recv_multipart()
    *_, manifest_json = message
    manifest_json = manifest_json.decode("utf-8")
    log.info("Entering dispatch with %s", manifest_json[:10])

    counter = 0
    while counter < 10_000:
        reposted, manifest_json = await repost(manifest_json)
        if reposted:
            log.info("Manifest reposted")
        try:
            manifest = json_loader.loads(manifest_json, target_class=Manifest)
        except (json.JSONDecodeError, ValidationError):
            log.error(
                "Validation Error for request with message %s",
                json.dumps(manifest_json, sort_keys=True, indent=4),
            )
            return None

        service = choose_service(manifest)

        if service is None or reposted:
            log.info("Waiting for a new message")
            message = await router.recv_multipart()
            *_, manifest_json = message
            manifest_json = manifest_json.decode("utf-8")
            continue

        log.info(
            "Dispatch task %d: treating manifest %s with states: %s",
            counter,
            manifest.id,
            manifest.states,
        )
        client = Client()
        manifest_json = json_dumper.dumps(manifest)
        log.info("dispatch is about to submit")
        await client.submit(service, [bytes(manifest_json, "utf-8")])
        log.info("Submitted manifest to service %s", service)
        reply_service, msg = await client.get()
        log.info("Got reply %s from service %s", msg[0][:10], reply_service)
        manifest_json = msg[-1].decode("utf-8")
        client.disconnect()
        manifest = json_loader.loads(manifest_json, target_class=Manifest)
        if manifest.step == len(manifest.route) - 1:
            log.info("End of the road for manifest %s", manifest.id)
            log.info("Waiting for a new message")
            message = await router.recv_multipart()
            *_, manifest_json = message
            manifest_json = manifest_json.decode("utf-8")

        counter += 1

    return manifest_json


def choose_service(manifest: Manifest) -> str | None:
    for state in manifest.states:
        if state.status == "errored":
            msg = f"manifest {manifest.id} is errored"
            log.warning(msg)
            return None
    if manifest.step < len(manifest.route):
        store = manifest.route[manifest.step + 1]
        return bytes(f"{store.id}", encoding="utf-8")  # _{idx:03d}
    log.info(
        "No local target service found for manifest %s",
        manifest.id,
    )

    return None


async def brocker(stop_event):
    scheduler = Scheduler(stop_event)
    await scheduler.on_recv_message()


async def clerk_coroutine(stop_event, clerk_class, conf, service, dry=False):
    """TODO"""

    async def run_clerk(*message):
        log.info("Clerk got a message")

        manifest_json = message[0].decode("utf-8")
        manifest = json_loader.loads(manifest_json, target_class=Manifest)
        log.info("%s got manifest %s", clerk_class.__name__, manifest.id)

        try:
            mngr = clerk_class(conf=conf, manifest=manifest)
        except Exception as e:
            log.error(
                "Manager from % failed to initialize", clerk_class.__name___, exc_info=e
            )
            return [bytes(manifest_json, "utf-8")]
        with mngr:
            log.info(
                "%s clerk instantiated, with state %s",
                clerk_class.__name__,
                mngr.state,
            )
            match mngr.state.status:
                case "started" | "expired":
                    log.info("There's work to do")
                    try:
                        manifest_json = mngr.routine(dry=dry)
                        log.info("%s clerk routine done", clerk_class.__name__)
                        mngr.set_state("checked")
                        manifest_json = json_dumper.dumps(mngr.manifest)

                    except Exception as e:
                        log.error("Clerk errored", exc_info=e)
                        mngr.set_state("errored")
                        manifest_json = json_dumper.dumps(mngr.manifest)
                        return [bytes(manifest_json, "utf-8")]

                case "errored":
                    msg = "Should not visit that state"
                    raise RuntimeError(msg)
                case "changed":
                    mngr.set_state("checked")
                    manifest_json = json_dumper.dumps(mngr.manifest)

        return [bytes(manifest_json, "utf-8")]

    worker = Worker(stop_event)
    await worker.run(service, run_clerk)


"""
"""
class_map = {
    #    "omero_waiter": OmeroWatcher, # TODO
    "omero_clerk": OmeroManager,
    "irods_clerk": iRODSManager,
    "file_clerk": FSManager,
    "rocrate_clerk": RoCrateManager,
    "omero_user_clerk": OmeroUserClerk,
    "atk_user_clerk": AuthentikClerk,
}


async def setup(conf: dict) -> None:
    log.info("Collecting coroutines")
    stop_event = asyncio.Event()
    coroutines = [brocker(stop_event)]

    # for _ in range(NUM_DISPATCH):
    coroutines.append(dispatch())

    if clerks := conf.get("clerks"):
        for role, clerk in clerks.items():
            store = clerk["store"]
            clerk_class = class_map[role]
            log.info("Registering %s's store clerk", store)
            service = bytes(f"{store}", "utf-8")
            for _ in range(NUM_WORKERS):
                # Spawn :)
                coroutines.append(
                    clerk_coroutine(stop_event, clerk_class, conf, service)
                )

    await asyncio.gather(*coroutines, return_exceptions=True)
