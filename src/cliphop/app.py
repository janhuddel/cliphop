"""FastAPI-Anwendung für cliphop."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager, suppress
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from .config import Config
from .db import Store
from .pubsub import Broadcaster
from .rendering import render_list, render_page

SSE_HEADERS = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
STATIC_DIR = Path(__file__).parent / "static"


def sse_event(data: str) -> str:
    """Formatiert Nutzlast als SSE-Nachricht (mehrzeilig erlaubt)."""
    return "".join(f"data: {line}\n" for line in data.split("\n")) + "\n"


async def stream_events(
    store: Store,
    broadcaster: Broadcaster,
    heartbeat: float,
    is_disconnected: Callable[[], Awaitable[bool]],
) -> AsyncIterator[str]:
    """Erst aktueller Listenstand, danach Änderungen, dazwischen Lebenszeichen."""
    queue = broadcaster.subscribe()
    try:
        yield sse_event(render_list(store.list_items()))
        while True:
            if await is_disconnected():
                break
            try:
                payload = await asyncio.wait_for(queue.get(), timeout=heartbeat)
            except TimeoutError:
                yield ": ping\n\n"
                continue
            yield sse_event(payload)
    finally:
        broadcaster.unsubscribe(queue)


async def tick_loop(interval: float, action: Callable[[], object]) -> None:
    """Ruft ``action`` wiederholt nach jeweils ``interval`` Sekunden auf."""
    while True:
        await asyncio.sleep(interval)
        action()


def prune_and_broadcast(store: Store, broadcaster: Broadcaster) -> int:
    """Entfernt abgelaufene Einträge und teilt dies den Clients mit."""
    removed = store.prune()
    if removed:
        broadcaster.publish(render_list(store.list_items()))
    return removed


def create_app(
    config: Config | None = None,
    store: Store | None = None,
    broadcaster: Broadcaster | None = None,
) -> FastAPI:
    config = config or Config.from_env()
    store = store or Store(config.db_path, config.ttl_seconds, config.max_items)
    broadcaster = broadcaster or Broadcaster()

    def list_response(error: str | None = None, status: int = 200) -> HTMLResponse:
        items = store.list_items()
        html = render_list(items, error=error)
        if error is None:
            broadcaster.publish(html)
        return HTMLResponse(html, status_code=status)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        task = asyncio.create_task(
            tick_loop(
                config.prune_interval_seconds,
                lambda: prune_and_broadcast(store, broadcaster),
            )
        )
        try:
            yield
        finally:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

    app = FastAPI(title="cliphop", lifespan=lifespan)
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/health")
    def health() -> PlainTextResponse:
        return PlainTextResponse("ok")

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon() -> FileResponse:
        # Browser fragen /favicon.ico auch ohne Link-Tag an; hier dasselbe SVG liefern.
        return FileResponse(STATIC_DIR / "favicon.svg", media_type="image/svg+xml")

    @app.get("/", response_class=HTMLResponse)
    def index() -> HTMLResponse:
        return HTMLResponse(render_page(store.list_items()))

    @app.post("/notes", response_class=HTMLResponse)
    async def add_note(content: str = Form("")) -> HTMLResponse:
        if not content.strip():
            return list_response(error="Bitte zuerst einen Text eingeben.", status=400)
        store.add(content)
        return list_response()

    @app.delete("/notes/{item_id}", response_class=HTMLResponse)
    async def delete_note(item_id: int) -> HTMLResponse:
        store.delete(item_id)
        return list_response()

    @app.patch("/notes/{item_id}", response_class=HTMLResponse)
    async def pin_note(item_id: int) -> HTMLResponse:
        if store.toggle_pin(item_id) is None:
            raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")
        return list_response()

    @app.post("/notes/clear", response_class=HTMLResponse)
    async def clear_notes(include_pinned: bool = Form(False)) -> HTMLResponse:
        store.clear(include_pinned=include_pinned)
        return list_response()

    @app.get("/events")
    async def events(request: Request) -> StreamingResponse:
        return StreamingResponse(
            stream_events(
                store,
                broadcaster,
                config.sse_heartbeat_seconds,
                request.is_disconnected,
            ),
            media_type="text/event-stream",
            headers=SSE_HEADERS,
        )

    return app


def main() -> None:
    import uvicorn

    uvicorn.run(
        "cliphop.app:create_app",
        factory=True,
        host="0.0.0.0",
        port=8000,
        workers=1,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
