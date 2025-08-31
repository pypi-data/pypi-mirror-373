import argparse
import atexit
import logging
import logging.config
import re
import shutil
import time
from asyncio import CancelledError, Queue, create_task, sleep
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from fnmatch import translate
from typing import Any, Optional
from uuid import UUID, uuid4
from weakref import WeakSet

import uvicorn
from fastapi import FastAPI, Request
from starlette.responses import StreamingResponse

from planar.config import PlanarConfig
from planar.logging import get_logger
from planar.sse.constants import SSE_ENDPOINT
from planar.sse.model import Event

logger = get_logger(__name__)


@dataclass(kw_only=True)
class EventWithTime:
    # Since event storage is volatile, "time" also uniquely identifies the event
    time: int = field(default_factory=time.monotonic_ns)
    event: Event


@dataclass(kw_only=True)
class Client:
    event_index: int = 0
    patterns: list[str] = field(default_factory=list)
    compiled_patterns: list[re.Pattern] = field(default_factory=list)
    queue: Queue[EventWithTime] = field(default_factory=Queue)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self):
        # Compile glob patterns to regex patterns
        self.compiled_patterns = []
        for pattern in self.patterns:
            translated = translate(pattern)
            logger.debug(
                "compiling glob pattern to regex", pattern=pattern, regex=translated
            )
            self.compiled_patterns.append(re.compile(translated))

    def forward(self, events: list[EventWithTime]):
        while self.event_index < len(events):
            event_time = events[self.event_index]
            event = event_time.event
            self.event_index += 1
            if not self.compiled_patterns:
                self.queue.put_nowait(event_time)
                continue
            for i, compiled_pattern in enumerate(self.compiled_patterns):
                logger.debug(
                    "matching event against pattern",
                    event_name=event.name,
                    pattern=self.patterns[i],
                )
                if compiled_pattern.fullmatch(event.name):
                    logger.debug(
                        "matched event against pattern",
                        event_name=event.name,
                        pattern=self.patterns[i],
                    )
                    self.queue.put_nowait(event_time)
                    break

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


events: list[EventWithTime] = []
clients: WeakSet[Client] = WeakSet()


# Periodically delete events older than 30 seconds.
async def cleanup_old_events():
    global events
    while True:
        await sleep(1)
        cutoff = time.monotonic_ns() - 30 * 1_000_000_000
        prune_index = None
        # find the index of the first event that is older than 30 seconds,
        # starting from the latest events
        prune_index = -1
        for i in range(len(events) - 1, -1, -1):
            event = events[i]
            if event.time < cutoff:
                prune_index = i
                break
        remove_count = prune_index + 1
        if remove_count > 0:
            for client in clients:
                client.event_index = max(0, client.event_index - remove_count)
            events = events[remove_count:]
            logger.debug("removed old events", count=remove_count)


@asynccontextmanager
async def lifespan(_: FastAPI):
    prune_task = create_task(cleanup_old_events())
    yield
    prune_task.cancel()
    try:
        await prune_task
    except CancelledError:
        pass


app = FastAPI(title="Planar SSE Hub", lifespan=lifespan)


@app.post("/push")
def push(event: Event):
    events.append(EventWithTime(event=event))
    for client in clients:
        client.forward(events)


@app.get(SSE_ENDPOINT)
async def sse(
    request: Request, subscribe: Optional[str] = None, new_events_only: bool = False
):
    # Get Last-Event-ID from headers
    last_event_id = request.headers.get("Last-Event-ID")

    client = Client(patterns=subscribe.split(",") if subscribe else [])
    clients.add(client)
    logger.debug("client connected", client_id=client.id)

    # Handle Last-Event-ID so that reconnects are handled correctly
    if last_event_id and not new_events_only:
        try:
            last_id = int(last_event_id)
            # Find the index of the event with the matching ID or the first one after it
            for i, event_time in enumerate(events):
                if event_time.time > last_id:
                    client.event_index = i
                    break
            logger.debug(
                "client resuming from event index",
                event_index=client.event_index,
                last_event_id=last_event_id,
            )
        except ValueError:
            logger.warning("invalid last-event-id format", last_event_id=last_event_id)

    if not new_events_only:
        client.forward(events)

    async def event_stream():
        try:
            while True:
                event_time = await client.queue.get()
                # I don't think ordering matters, but in the docs ids always
                # come last, so repeat that here
                yield f"data: {event_time.event.model_dump_json()}\nid: {event_time.time}\n\n"
        except CancelledError:
            logger.debug("client disconnected", client_id=client.id)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


def builtin_run(server_url: str, socket_dir: str, planar_config_dict: dict[str, Any]):
    # we only use this to configure logging
    config = PlanarConfig.model_validate(planar_config_dict)
    config.configure_logging()

    def cleanup():
        shutil.rmtree(socket_dir)

    # ensure the socket directory is removed on exit
    atexit.register(cleanup)

    # explicitly set 1 worker since this is going to aggregate all events
    # we have to pass log_config=None to prevent uvicorn from trying to
    # configure logging by itself
    uvicorn.run(app, uds=server_url, workers=1, log_config=None)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", default=8888, type=int)
    return parser.parse_args()


def main():
    args = parse_args()
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(
        level=logging.DEBUG, format="[%(levelname)s] %(asctime)s - %(message)s"
    )
    uvicorn.run(app, host=args.host, port=args.port, workers=1)


if __name__ == "__main__":
    main()
