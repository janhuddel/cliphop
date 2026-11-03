from fastapi.testclient import TestClient

from cliphop.app import create_app
from cliphop.config import Config
from cliphop.db import Store
from cliphop.pubsub import Broadcaster

FIXED = 1_700_000_000.0


def build_client():
    config = Config(
        db_path=":memory:",
        sse_heartbeat_seconds=0.05,
        prune_interval_seconds=3600,
    )
    store = Store(":memory:", config.ttl_seconds, config.max_items, clock=lambda: FIXED)
    broadcaster = Broadcaster()
    app = create_app(config=config, store=store, broadcaster=broadcaster)
    return TestClient(app), store, broadcaster


def test_health():
    client, _, _ = build_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.text == "ok"


def test_static_assets_served():
    client, _, _ = build_client()
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/htmx.min.js").status_code == 200
    assert client.get("/static/favicon.svg").status_code == 200


def test_manifest_served():
    client, _, _ = build_client()
    response = client.get("/static/manifest.webmanifest")
    assert response.status_code == 200
    payload = response.json()
    assert payload["scope"] == "/"
    assert payload["start_url"] == "/"
    assert payload["display"] == "standalone"
    assert {icon["sizes"] for icon in payload["icons"]} == {"180x180", "512x512"}


def test_index_links_manifest_and_icons():
    client, _, _ = build_client()
    body = client.get("/").text
    assert 'rel="manifest" href="/static/manifest.webmanifest"' in body
    assert 'rel="apple-touch-icon"' in body
    assert "/static/icon-180.png" in body
    assert 'name="theme-color"' in body
    assert 'name="apple-mobile-web-app-capable" content="yes"' in body
    assert 'name="apple-mobile-web-app-status-bar-style"' in body


def test_index_viewport_fit_cover():
    client, _, _ = build_client()
    assert 'name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"' in client.get("/").text


def test_style_respects_safe_areas():
    client, _, _ = build_client()
    body = client.get("/static/style.css").text
    for inset in ("top", "right", "bottom", "left"):
        assert f"env(safe-area-inset-{inset})" in body


def test_favicon_ico_served():
    client, _, _ = build_client()
    response = client.get("/favicon.ico")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")


def test_index_links_favicon():
    client, _, _ = build_client()
    assert 'rel="icon"' in client.get("/").text
    assert "/static/favicon.svg" in client.get("/").text


def test_index_empty_state():
    client, _, _ = build_client()
    response = client.get("/")
    assert response.status_code == 200
    assert "Noch keine Einträge" in response.text


def test_add_note():
    client, store, _ = build_client()
    response = client.post("/notes", data={"content": "hallo welt"})
    assert response.status_code == 200
    assert "hallo welt" in response.text
    assert [i.content for i in store.list_items()] == ["hallo welt"]


def test_add_empty_is_rejected():
    client, store, _ = build_client()
    response = client.post("/notes", data={"content": "   "})
    assert response.status_code == 400
    assert "Bitte zuerst" in response.text
    assert store.list_items() == []


def test_rendered_order_newest_first():
    client, store, _ = build_client()
    store.add("aelter")
    store.add("neuer")
    body = client.get("/").text
    assert body.index("neuer") < body.index("aelter")


def test_delete_note():
    client, store, _ = build_client()
    item = store.add("weg damit")
    response = client.delete(f"/notes/{item.id}")
    assert response.status_code == 200
    assert store.list_items() == []
    assert "Noch keine Einträge" in response.text


def test_pin_toggle_via_patch():
    client, store, _ = build_client()
    item = store.add("merken")
    response = client.patch(f"/notes/{item.id}")
    assert response.status_code == 200
    assert "gepinnt" in response.text
    assert store.list_items()[0].pinned is True


def test_pin_missing_is_404():
    client, _, _ = build_client()
    assert client.patch("/notes/999").status_code == 404


def test_clear_unpinned_only():
    client, store, _ = build_client()
    store.add("weg")
    keep = store.add("bleibt")
    store.toggle_pin(keep.id)
    response = client.post("/notes/clear", data={})
    assert response.status_code == 200
    assert [i.content for i in store.list_items()] == ["bleibt"]


def test_clear_including_pinned():
    client, store, _ = build_client()
    item = store.add("bleibt")
    store.toggle_pin(item.id)
    response = client.post("/notes/clear", data={"include_pinned": "true"})
    assert response.status_code == 200
    assert store.list_items() == []


def test_add_broadcasts_new_state():
    client, _, broadcaster = build_client()
    queue = broadcaster.subscribe()
    client.post("/notes", data={"content": "live"})
    assert "live" in queue.get_nowait()


def test_events_stream_snapshot_and_heartbeat():
    client, store, _ = build_client()
    store.add("live")
    with client.stream("GET", "/events") as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        got_snapshot = False
        got_heartbeat = False
        for line in response.iter_lines():
            if line.startswith("data:") and "live" in line:
                got_snapshot = True
            if line.strip() == ": ping":
                got_heartbeat = True
            if got_snapshot and got_heartbeat:
                break
        assert got_snapshot
        assert got_heartbeat
