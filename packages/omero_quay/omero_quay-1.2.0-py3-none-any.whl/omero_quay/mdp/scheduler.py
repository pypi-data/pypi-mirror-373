from __future__ import annotations

import asyncio
import collections
import concurrent
import contextlib
import datetime as dt
import logging
import uuid

import zmq
import zmq.asyncio


class Message:
    def __init__(self, client_id, message):
        self.date_added = dt.datetime.utcnow()
        self.client_id = client_id
        self.message = message


class SchedulerCode:
    WORKER = b"MDPW01"
    CLIENT = b"MDPC01"
    READY = bytes([1])
    REQUEST = bytes([2])
    REPLY = bytes([3])
    HEARTBEAT = bytes([4])
    DISCONNECT = bytes([5])


class Scheduler:
    DEFAULT_PROTOCOL = "tcp"
    DEFAULT_PORT = 5555
    DEFAULT_HOSTNAME = "0.0.0.0"

    def __init__(
        self,
        stop_event,
        protocol=DEFAULT_PROTOCOL,
        port=DEFAULT_PORT,
        hostname=DEFAULT_HOSTNAME,
        loop=None,
    ):
        self.stop_event = stop_event
        self.loop = loop or asyncio.get_event_loop()
        self.logger = logging.getLogger(f"omero_quay.mdp.{__name__}")
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        self.logger.info(f"Binding ZMQ socket client to {protocol}://{hostname}:{port}")
        self.socket.bind(f"{protocol}://{hostname}:{port}")
        self.messages = {}
        self.workers = {}
        self.services = collections.defaultdict(
            lambda: {"workers": set(), "queue": asyncio.Queue(), "task": None}
        )

    async def _handle_client_message(self, client_id, multipart_message):
        service, *message_data = multipart_message
        self.logger.debug(
            f"adding client {client_id} message for service {service} to queue"
        )
        message_uuid = uuid.uuid4().bytes
        message = Message(client_id, message_data)
        self.messages[message_uuid] = message
        await self.services[service]["queue"].put(message_uuid)

    async def _next_worker(self, service):
        import random

        return random.sample(service["workers"], 1)[0]  # scheduling logic
        # return service['workers'][0]

    async def _handle_service_queue(self, service):
        counter = 0
        try:
            while True:
                message_uuid = await service["queue"].get()
                message = self.messages[message_uuid]
                worker_id = await self._next_worker(service)
                counter += 1
                # print(f"[Scheduler] Count {counter} sent to worker {worker_id}")
                self.workers[worker_id]["messages"].add(message_uuid)
                await self.socket.send_multipart(
                    [
                        worker_id,
                        b"",
                        SchedulerCode.WORKER,
                        SchedulerCode.REQUEST,
                        message_uuid,
                        b"",
                        *message.message,
                    ]
                )
                service["queue"].task_done()
        except (asyncio.CancelledError, RuntimeError):
            self.logger.info("stopping worker for service")

    async def _handle_worker_message(self, worker_id, multipart_message):
        message_type = multipart_message[0]
        match message_type:
            case SchedulerCode.READY:
                service_name = multipart_message[1]
                service = self.services[service_name]
                self.logger.info(
                    f"adding worker {worker_id} for service {service_name}"
                )
                self.workers[worker_id] = {"service": service_name, "messages": set()}
                service["workers"].add(worker_id)
                if len(service["workers"]) == 1:
                    service["task"] = asyncio.ensure_future(
                        self._handle_service_queue(service)
                    )
            case SchedulerCode.REPLY:
                message_uuid = multipart_message[1]
                self.workers[worker_id]["messages"].remove(message_uuid)
                message = self.messages.pop(message_uuid)
                self.logger.debug(
                    f"sending client {message.client_id} message response from worker {worker_id}"
                )
                # print(
                #     f"[Scheduler] message done from worker {worker_id} for client {message.client_id}"
                # )
                await self.socket.send_multipart(
                    [
                        message.client_id,
                        b"",
                        SchedulerCode.CLIENT,
                        self.workers[worker_id]["service"],
                        *multipart_message[3:],
                    ]
                )
            case SchedulerCode.HEARTBEAT:
                self.logger.debug("responding with heartbeat")
                await self.socket.send_multipart(
                    [worker_id, b"", SchedulerCode.WORKER, SchedulerCode.HEARTBEAT]
                )
            case SchedulerCode.DISCONNECT:
                if worker_id in self.workers:
                    worker = self.workers[worker_id]
                    service = self.services[worker["service"]]
                    if len(service["workers"]) == 1:  # last worker
                        self.logger.info(
                            f'canceling {worker["service"]} service queue task'
                        )
                        service["task"].cancel()

                        with contextlib.suppress(concurrent.futures.CancelledError):
                            await service["task"]
                        service["task"] = None
                    self.logger.info(
                        f'removing worker {worker_id} for service {worker["service"]} - rescheduling {len(worker["messages"])} messages'
                    )
                    service["workers"].remove(worker_id)
                    for message in worker["messages"]:
                        await service["queue"].put(message)
                    self.workers.pop(worker_id)

    async def on_recv_message(self):
        while not self.stop_event.is_set():
            multipart_message = await self.socket.recv_multipart()
            client_id, _1, message_sender, *message = multipart_message
            if message_sender == SchedulerCode.WORKER:
                await self._handle_worker_message(client_id, message)
            elif message_sender == SchedulerCode.CLIENT:
                await self._handle_client_message(client_id, message)
            else:
                raise ValueError()

    def run(self):
        self.loop.run_until_complete(self.on_recv_message())

    def disconnect(self):
        self.stop_event.set()
        self.socket.close()
