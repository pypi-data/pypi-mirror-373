from __future__ import annotations

import asyncio
import json
import logging

import zmq
import zmq.asyncio
from linkml_runtime.dumpers import json_dumper
from linkml_runtime.loaders import json_loader
from pydantic import ValidationError
from tornado import web
from zmq.asyncio import Context

from omero_quay.clients.http import post_request
from omero_quay.core.config import get_conf
from omero_quay.core.connect import mongo_client

from .manifest import Manifest

log = logging.getLogger("omero_quay")


def parse_mongo_query(request):
    log.debug("Query arguments %s", request.query_arguments)
    req_args = {
        k: json.loads(v[0].decode("utf-8")) for k, v in request.query_arguments.items()
    }
    log.debug("Query parameters %s", req_args)
    kwargs = {}
    if filter_ := req_args.get("filter"):
        kwargs["filter"] = filter_
    if limit := req_args.get("limit"):
        kwargs["limit"] = int(limit)
    if projection := req_args.get("projection"):
        kwargs["projection"] = projection
    if sort := req_args.get("sort"):
        field, order = sort
        kwargs["sort"] = [(field, int(order))]
    else:
        # Sort by descending creation date by default
        kwargs["sort"] = [("timestamps.0", -1)]

    log.debug("Mongo kwargs: %s", kwargs)

    return kwargs


class MongoHandler(web.RequestHandler):
    async def get(self) -> None:
        db = self.settings["db"]
        kwargs = parse_mongo_query(self.request)
        log.debug("Got request with parameters: %s", kwargs)
        cursor = db.manifests.find(**kwargs)
        documents = await cursor.to_list(length=30)

        log.debug("found %d manifests", len(documents))
        retrieved_manifests = []
        for manifest_dict in documents:
            manifest_dict.pop("_id")
            manifest = Manifest(**manifest_dict)
            retrieved_manifests.append(manifest)

        manifest_jsons = ", ".join(
            json_dumper.dumps(man) for man in retrieved_manifests
        )
        dumped = f"[{manifest_jsons}]"
        self.write(dumped)

    async def post(self) -> None:
        log.info("MongoHandler got a post message")
        manifest = None
        if msg := self.request.body:
            try:
                manifest_json = msg.decode("utf-8")
                manifest = json_loader.loads(manifest_json, target_class=Manifest)

            except (json.JSONDecodeError, ValidationError) as e:
                log.error(
                    "Validation Error in http handler for  message %s", msg, exc_info=e
                )
                self.write("400")
                return
            except FileNotFoundError as e:
                log.error("tries to parse as a file %s", msg, exc_info=e)
                self.write("400")
                return
            except Exception as e:
                log.error("Other error in http handler for message %s", msg, exc_info=e)
                self.write("400")
                return
        db = self.settings["db"]
        result = await db.manifests.update_one(
            {"_id": manifest.id}, {"$set": manifest.model_dump()}, upsert=True
        )
        if result.matched_count:
            log.debug("Updated manifest %s in DB", manifest.id)
        else:
            log.debug("Inserted new manifest %s in DB", manifest.id)
        self.write(json_dumper.dumps(manifest))


# TODO : authenticate users for those requests
# Currently the request is behind atk authentication
# Will not work for API access
class Handler(web.RequestHandler):
    """
        curl -X POST -H "Content-Type: application/json" \
           -d '{"investigation": "group1", "study": "study0"}' \
           http://localhost:8888
    """

    async def get(self) -> None:
        db = self.settings["db"]
        kwargs = parse_mongo_query(self.request)
        log.debug("Got request with parameters: %s", kwargs)
        cursor = db.manifests.find(**kwargs)
        documents = await cursor.to_list(length=30)
        log.debug("found %d manifests", len(documents))
        self.write(json.dumps(documents))

    async def post(self) -> None:
        """
            curl -X POST -H "Content-Type: application/json" \
               -d '{"investigation": "group1", "study": "study0"}' \
               http://localhost:8888
        """

        log.info("Handler got a post message")
        if msg := self.request.body:
            try:
                manifest_json = msg.decode("utf-8")
                _ = json_loader.loads(manifest_json, target_class=Manifest)

            except (json.JSONDecodeError, ValidationError) as e:
                log.error(
                    "Validation Error in http handler for  message %s", msg, exc_info=e
                )
                self.write("400")
                return
            # When json_loader.loads can't parse the message, it
            # tries to open it as a file, hillarity ensues
            except FileNotFoundError:
                log.error("tries to parse as a file %s", msg)  # , exc_info=e)
                self.write("400")
                return
            except Exception as e:
                log.error("Other error in http handler for message %s", msg, exc_info=e)
                self.write("400")
                return

            reposted, manifest_json = await repost(manifest_json)
            if not reposted:
                await self._send(manifest_json)
            self.write(manifest_json)
            log.info("Exiting http handler post method")

    async def _send(self, manifest_json):
        context = Context.instance()

        with context.socket(zmq.REQ) as sender:
            identity = bytes("dispatch", "utf-8")
            sender.setsockopt(zmq.IDENTITY, identity)
            sender.connect("tcp://localhost:5556")
            await sender.send_string(manifest_json)
            #  Don't wait for the reply
            # await sender.recv_string()
            # log.info("handler got reply from %d", out_port)


async def repost(manifest_json):
    manifest = json_loader.loads(manifest_json, target_class=Manifest)
    conf = get_conf()
    if manifest.route and manifest.step < len(manifest.route):
        trgt_store = manifest.route[manifest.step + 1]
    else:
        return False, manifest_json

    if trgt_store.post_url:
        current_host = conf["quay"]["host"]
        log.debug("current host: %s, target_host: %s", current_host, trgt_store.host)
        if current_host == trgt_store.host:
            return False, manifest_json

        log.info("hosts differ, reposting manifest %s", manifest.id)
        log.info("submitting to target host %s", trgt_store.post_url)
        rep = post_request(manifest_json, post_url=trgt_store.post_url)
        log.info("Got answer %s from target host", rep)
        return True, manifest_json
    return False, manifest_json


async def tornado_server():
    log.info("Connecting to mongo")

    conf = get_conf()
    if "mongo" in conf:
        client = mongo_client(conf, is_async=True)
        db = client.quay
    else:
        db = None
    log.info("Starting web application")
    application = web.Application([(r"/", Handler), (r"/mongo", MongoHandler)], db=db)
    application.listen(8888)
    await asyncio.Event().wait()


def tornado_server_process():
    asyncio.run(tornado_server())
