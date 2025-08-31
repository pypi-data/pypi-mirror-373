import os
import tempfile
import uuid
from asyncio import (
    CancelledError,
    Queue,
    QueueFull,
    Task,
    create_task,
    current_task,
    sleep,
)
from contextlib import asynccontextmanager
from multiprocessing import Process
from typing import Any
from weakref import WeakSet

import httpx
from fastapi import APIRouter, Request
from starlette.responses import StreamingResponse

from planar.config import PlanarConfig
from planar.logging import get_logger
from planar.sse.constants import SSE_ENDPOINT
from planar.sse.hub import builtin_run
from planar.sse.model import Event

logger = get_logger(__name__)


def parse_hub_url(
    hub_url: str,
) -> tuple[httpx.AsyncHTTPTransport | None, str]:
    transport = None
    if hub_url[0] == "/":
        transport = httpx.AsyncHTTPTransport(uds=hub_url)
        # Use a dummy server URL for formatting the target URL.
        # The transport will ignore it and connect to the domain socket
        hub_url = "http://planar-sse"
    return transport, hub_url


def get_builtin_hub_socket_path():
    # This env var trick has two purposes:
    #
    #   - Generate a unique socket path
    #   - Distribute the same socket path to all workers.
    #
    # Initially the env var will not be set, so we generate the uuid
    # and set it. When uvicorn spawns workers, they will inherit the
    # parent environment and use it instead of generating their own.
    builtin_hub_uuid = os.getenv("PLANAR_BUILTIN_SSE_UUID", "")
    if builtin_hub_uuid == "":
        builtin_hub_uuid = str(uuid.uuid4())
        os.environ["PLANAR_BUILTIN_SSE_UUID"] = builtin_hub_uuid
    return f"{tempfile.gettempdir()}/planar-sse-{builtin_hub_uuid}/socket"


class SSEProxy:
    def __init__(
        self,
        config: PlanarConfig,
    ):
        sse_hub = config.sse_hub
        self.config = config
        self.enable_builtin_hub = False
        self.hub_url = ""
        self.stream_tasks: WeakSet[Task] = WeakSet()

        if isinstance(sse_hub, str):
            # Connect to a separate SSE hub listening on a TCP address
            self.hub_url = sse_hub
        elif sse_hub is True:
            # Use builtin hub spawned as a subprocess listening on an UNIX socket.
            self.enable_builtin_hub = True
            self.hub_url = get_builtin_hub_socket_path()

        self.builtin_process: Process | None = None
        self.router = APIRouter()
        self.queue: Queue[Event] = Queue(maxsize=1000)
        self.forward_task: Task | None = None

        if self.hub_url:
            self.setup_proxy_endpoint()

    def push(self, name: str, payload: dict[str, Any]):
        try:
            self.queue.put_nowait(Event(name=name, payload=payload))
        except QueueFull:
            # not processing events fast enough, so just ignore it
            logger.warning("sse proxy queue is full, dropping event", event_name=name)

    def start_builtin_hub(self):
        assert self.hub_url[0] == "/"
        socket_dir = os.path.dirname(self.hub_url)
        logger.debug("attempting to create socket directory", socket_dir=socket_dir)
        try:
            # try to create the socket directory, only one of the workers will
            # succeed
            os.mkdir(socket_dir)
            logger.debug("socket directory created", socket_dir=socket_dir)
        except FileExistsError:
            # another worker created the directory first, ignore
            logger.debug("socket directory already exists", socket_dir=socket_dir)
            return

        # start the builtin SSE hub in a separate process
        logger.info(
            "starting builtin sse hub process for socket", socket_url=self.hub_url
        )
        self.builtin_process = Process(
            target=builtin_run,
            args=(self.hub_url, socket_dir, self.config.model_dump()),
        )
        self.builtin_process.start()

    def start(self):
        logger.debug(
            "sseproxy start called",
            hub_url=self.hub_url,
            enable_builtin=self.enable_builtin_hub,
        )
        if not self.hub_url:
            raise ValueError("hub_url is not set")

        if self.enable_builtin_hub:
            self.start_builtin_hub()

        async def forward():
            transport, hub_url = parse_hub_url(self.hub_url)
            forward_url = f"{hub_url}/push"
            logger.debug("sse event forwarding task started", url=forward_url)
            async with httpx.AsyncClient(transport=transport) as client:
                while True:
                    event = await self.queue.get()
                    logger.debug(
                        "got event from queue to forward", event_name=event.name
                    )
                    while True:
                        try:
                            await client.post(
                                forward_url,
                                content=event.model_dump_json(),
                                headers={"Content-Type": "application/json"},
                            )
                            logger.info(
                                "successfully forwarded event",
                                event_name=event.name,
                                url=forward_url,
                            )
                            break
                        except Exception:
                            logger.exception(
                                "exception while forwarding sse event to hub, will retry"
                            )
                            await sleep(5)

        self.forward_task = create_task(forward())
        logger.info("sse event forwarding task created")

    async def stop(self):
        logger.debug("sseproxy stop called")
        if self.forward_task:
            logger.info("cancelling sse event forwarding task")
            self.forward_task.cancel()
            try:
                await self.forward_task
            except CancelledError:
                logger.debug("sse event forwarding task cancelled")
                pass

        for stream_task in self.stream_tasks:
            logger.debug("cancelling sse stream task", task=stream_task.get_name())
            stream_task.cancel()

        if self.builtin_process:
            # when using multiple workers, only one worker will have started the
            # builtin hub. That's why we check for self.builtin_process instead of
            # self.enable_builtin_hub. Also helps with type checking.
            logger.info("terminating builtin sse hub process")
            self.builtin_process.terminate()

    def setup_proxy_endpoint(self):
        @self.router.get("/")
        async def proxy(request: Request):
            logger.debug(
                "sse proxy endpoint called",
                query=request.url.query,
                headers=dict(request.headers),
            )
            async with self.connect(request.url.query, dict(request.headers)) as (
                status,
                headers,
                stream,
            ):
                return StreamingResponse(
                    stream(),
                    status_code=status,
                    headers=headers,
                )

        return proxy  # dummy return to prevent unused warning

    @asynccontextmanager
    async def connect(self, query: str = "", headers: dict[str, str] = {}):
        logger.debug("sseproxy connect called", query=query, headers=headers)

        transport, hub_url = parse_hub_url(self.hub_url)

        client = httpx.AsyncClient(
            transport=transport, base_url=hub_url, timeout=httpx.Timeout(None)
        )

        while True:
            try:
                # Construct the target URL
                url = httpx.URL(
                    path=SSE_ENDPOINT,
                    query=query.encode(),
                )

                # Build the outgoing request
                proxy_request = client.build_request(
                    method="GET",
                    url=url,
                    headers=headers,
                )

                # Send the request and stream the response
                response = await client.send(proxy_request, stream=True)
                logger.debug("connected to sse hub", hub_url=hub_url)

                async def stream(lines: bool = False):
                    stream_task = current_task()
                    assert stream_task
                    self.stream_tasks.add(stream_task)
                    try:
                        async for chunk in (
                            response.aiter_lines() if lines else response.aiter_bytes()
                        ):
                            yield chunk
                    except CancelledError:
                        logger.debug("sse stream task cancelled")
                        raise
                    finally:
                        await client.aclose()

                yield response.status_code, dict(response.headers), stream
                break
            except Exception:
                logger.exception("exception while connecting to sse hub, will retry")
                await sleep(5)
