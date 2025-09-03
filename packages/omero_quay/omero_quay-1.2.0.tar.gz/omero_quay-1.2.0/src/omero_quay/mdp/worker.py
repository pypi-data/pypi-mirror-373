from __future__ import annotations

import asyncio
import datetime as dt
import logging

import zmq
import zmq.asyncio

from .scheduler import SchedulerCode

log = logging.getLogger("omero_quay.mdp.{__name__}")


class Worker:
    DEFAULT_PROTOCOL = "tcp"
    DEFAULT_PORT = 5555
    DEFAULT_HOSTNAME = "0.0.0.0"

    def __init__(
        self,
        stop_event,
        heartbeat_interval=2,
        heartbeat_timeout=10,
        protocol=DEFAULT_PROTOCOL,
        port=DEFAULT_PORT,
        hostname=DEFAULT_HOSTNAME,
        loop=None,
    ):
        self.stop_event = stop_event
        self.loop = loop or asyncio.get_event_loop()
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.uri = f"{protocol}://{hostname}:{port}"
        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_timeout = heartbeat_timeout
        self.heartbeat_last_response = dt.datetime.utcnow()
        self.service = None
        self.service_handler = None
        self.queued_messages = asyncio.Queue()

    async def _handle_send_heartbeat(self):
        while not self.stop_event.is_set():
            if not self.socket.closed:
                log.debug("sending heartbeat")
                await self.socket.send_multipart(
                    [b"", SchedulerCode.WORKER, SchedulerCode.HEARTBEAT]
                )
            await asyncio.sleep(self.heartbeat_interval)

    async def _handle_check_heartbeat(self):
        while not self.stop_event.is_set():
            previous_heartbeat_check = dt.datetime.utcnow()
            await asyncio.sleep(self.heartbeat_timeout)
            if (
                not self.socket.closed
                and self.heartbeat_last_response < previous_heartbeat_check
            ):
                log.info(
                    f"no response from broker in {self.heartbeat_timeout} seconds -- reconnecting"
                )
                await self.disconnect()
                await self.connect()

    async def _handle_queued_messages(self):
        counter = 0
        while not self.stop_event.is_set():
            client_id, message = await self.queued_messages.get()
            log.info("latest message from client %s", client_id)

            result = await self.service_handler(*message)
            counter += 1
            log.info(
                f"[ Worker  ] Counter {counter:5} completed Queue size: {self.queued_messages.qsize():5}"
            )
            log.info("Sending response to client %s", client_id)
            await self.socket.send_multipart(
                [
                    b"",
                    SchedulerCode.WORKER,
                    SchedulerCode.REPLY,
                    client_id,
                    b"",
                    *result,
                ]
            )
            log.info("\n\n\n\n Handling done \n\n\n\n")
            self.queued_messages.task_done()

    async def _on_recv_message(self):
        while not self.stop_event.is_set():
            multipart_message = await self.socket.recv_multipart()
            message_type = multipart_message[2]
            match message_type:
                case SchedulerCode.REQUEST:
                    _, _, message_type, client_id, _, *message = multipart_message
                    log.debug("broker sent request message")
                    await self.queued_messages.put((client_id, message))
                    self.heartbeat_last_response = dt.datetime.utcnow()
                case SchedulerCode.HEARTBEAT:
                    log.debug("broker response heartbeat")
                    self.heartbeat_last_response = dt.datetime.utcnow()
                case SchedulerCode.DISCONNECT:
                    log.info("broker requests disconnect and reconnect")
                    await self.disconnect()
                    await self.connect()
                case _:
                    raise ValueError()  # unknown event type

    async def run(self, service, service_handler):
        self.service = service
        self.service_handler = service_handler
        await self.connect()
        await asyncio.gather(
            self._handle_send_heartbeat(),
            self._handle_check_heartbeat(),
            self._handle_queued_messages(),
            self._on_recv_message(),
        )
        await self.disconnect()

    async def connect(self):
        log.info(f"connecting ZMQ socket to {self.uri}")
        self.socket.connect(self.uri)
        await self.socket.send_multipart(
            [b"", SchedulerCode.WORKER, SchedulerCode.READY, self.service]
        )

    async def disconnect(self):
        log.info(f"disconnecting zmq socket from {self.uri}")
        await self.socket.send_multipart(
            [b"", SchedulerCode.WORKER, SchedulerCode.DISCONNECT]
        )
        self.socket.disconnect(self.uri)
