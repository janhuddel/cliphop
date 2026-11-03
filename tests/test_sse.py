import asyncio

from cliphop.app import prune_and_broadcast, sse_event, stream_events, tick_loop
from cliphop.db import Store
from cliphop.pubsub import Broadcaster

FIXED = 1_700_000_000.0


def make_store(ttl=3600, clock=None):
    return Store(
        ":memory:",
        ttl_seconds=ttl,
        max_items=50,
        clock=clock or (lambda: FIXED),
    )


async def connected() -> bool:
    return False


def test_sse_event_multiline():
    assert sse_event("a\nb") == "data: a\ndata: b\n\n"


def test_first_event_is_current_list():
    store = make_store()
    store.add("hallo")
    broadcaster = Broadcaster()

    async def run():
        stream = stream_events(store, broadcaster, 999, connected)
        first = await anext(stream)
        await stream.aclose()
        return first

    out = asyncio.run(run())
    assert out.startswith("data:")
    assert "hallo" in out


def test_heartbeat_in_idle():
    store = make_store()
    broadcaster = Broadcaster()

    async def run():
        stream = stream_events(store, broadcaster, 0.01, connected)
        await anext(stream)  # Snapshot
        beat = await anext(stream)  # Lebenszeichen
        await stream.aclose()
        return beat

    assert asyncio.run(run()) == ": ping\n\n"


def test_delivers_published_update():
    store = make_store()
    broadcaster = Broadcaster()

    async def run():
        stream = stream_events(store, broadcaster, 999, connected)
        await anext(stream)  # Snapshot
        broadcaster.publish("<div>neu</div>")
        payload = await anext(stream)
        await stream.aclose()
        return payload

    assert "neu" in asyncio.run(run())


def test_prune_and_broadcast_removes_and_notifies():
    clock = {"t": FIXED}
    store = make_store(ttl=10, clock=lambda: clock["t"])
    broadcaster = Broadcaster()
    store.add("alt")  # created_at = FIXED
    queue = broadcaster.subscribe()

    clock["t"] = FIXED + 100  # älter als die TTL
    removed = prune_and_broadcast(store, broadcaster)

    assert removed == 1
    assert store.list_items() == []
    assert "alt" not in queue.get_nowait()


def test_tick_loop_calls_action():
    calls = []

    async def run():
        task = asyncio.create_task(tick_loop(0.01, lambda: calls.append(1)))
        await asyncio.sleep(0.05)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    asyncio.run(run())
    assert calls
