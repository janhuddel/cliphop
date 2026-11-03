# cliphop

Private Web-App zum schnellen Austausch kurzer Textnotizen zwischen eigenen
Geräten. Läuft im Homelab in einem Container hinter HAProxy → Traefik; der
Hostname `cliphop.rohwer.sh` löst per Split-Horizon-DNS nur im LAN auf.
Der neueste Eintrag ist der „aktuelle" Slot, darunter der Verlauf.

**Vor der Arbeit lesen:** `openspec/changes/add-cliphop/` (Proposal, Design,
Specs, Tasks) und `docs/DEPLOYMENT.md`. Der Change ist die Quelle der Wahrheit —
nicht neu erfragen, was dort schon entschieden ist.

## Arbeitsweise

- **Sprache:** Mit dem Nutzer sprichst du Deutsch; Code, Identifier, Kommentare
  und Commit-Nachrichten auf Englisch.
- **Committen nur auf Anfrage.** Nichts pushen, ohne dass der Nutzer es sagt.
- **OpenSpec:** Neue Arbeit beginnt als Change unter `openspec/changes/`
  (`/opsx-propose`, `/opsx-apply`, `/opsx-archive`). Keine Change-Verzeichnisse
  von Hand anlegen.
- **Secrets:** Es gibt derzeit keine. Sollten welche dazukommen (OIDC), gehören
  sie in eine gitignorierte `.env` und nie in Chat, Commit oder Logs.

## Stack und Befehle

Python 3.12 via `uv`; FastAPI + Jinja2 + HTMX + SQLite; ein Container, genau
**ein** uvicorn-Worker.

```sh
uv sync
uv run pytest
uv run python scripts/bump_version.py <version>   # setzt die Version überall und ruft `uv lock`
CLIPHOP_DB=./data/cliphop.db uv run uvicorn cliphop.app:create_app --factory --reload
docker build --build-arg VERSION=<version> -t oci.rohwer.sh/cliphop:<version> .
```

## Randbedingungen und Fallstricke

- **Ein Worker.** Die Live-Updates laufen über Pub/Sub im Prozess
  (`cliphop/pubsub.py`). Mehrere Worker bräuchten einen externen Vermittler.
- **SSE ungepuffert.** Auf dem Traefik-Router für diese App keine `compress`-
  oder `buffering`-Middleware; der Server sendet alle ~20 s ein Heartbeat.
- **HTMX und dynamisches Markup.** Per SSE gesetztes `innerHTML` verarbeitet
  HTMX nicht von selbst — `htmx.process()` aufrufen, sonst sind `hx-patch`/
  `hx-delete` an neu gerenderten Buttons wirkungslos (siehe `static/app.js`).
- **Fachlogik:** Einträge sind unveränderlich (Ändern = löschen + neu ablegen);
  Pin schützt vor der TTL; die Obergrenze `CLIPHOP_MAX_ITEMS` gilt nur für
  ungepinnte Einträge.
- **Clipboard** funktioniert nur im Secure Context (`https://` oder
  `localhost`); sonst greift ein Fallback ohne Zwischenablage.
- **Templates** lädt Jinja bei jeder Anfrage neu — UI-Änderungen sind ohne
  Neustart sichtbar. Statische Assets (inkl. HTMX) liegen lokal, kein CDN.
- **Version.** Kanonisch ist `pyproject.toml`. Dieselbe Version tragen außerdem
  `Dockerfile` (`ARG VERSION`), `compose.yaml` (Image-Tag),
  `src/cliphop/__init__.py` (`__version__`), die beiden Beispielbefehle in
  `docs/DEPLOYMENT.md` und `uv.lock`. Alle Stellen gemeinsam setzen:
  `uv run python scripts/bump_version.py <version>` (ruft danach `uv lock`);
  `uv run python scripts/bump_version.py --check` (läuft auch in `uv run pytest`)
  schlägt bei jeder Abweichung fehl.

## Deployment

Siehe `docs/DEPLOYMENT.md`. Kurz: Image nach `oci.rohwer.sh/cliphop:<version>`
bauen und pushen, Service aus `compose.yaml` im bestehenden Stack starten.
