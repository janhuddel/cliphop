# Design

## Context

Siehe `proposal.md` für Motivation und Umfang. Diese Datei erklärt das *Wie*.

`cliphop` ist eine neue, sehr kleine Web-App. Der umgebende Betrieb ist dagegen bereits etabliert und wird übernommen, nicht neu erfunden:

- Kette **Browser → HAProxy (TLS) → Traefik (Ingress) → App**; Traefik routet per Host-Regel über Labels.
- Öffentliche Adresse aus `BASE_URL` ableiten (wie in `vrp`), nicht aus Proxy-Headern.
- Hostname `cliphop.rohwer.sh` löst per Split-Horizon-DNS **nur im LAN** auf — daher ist die App nicht öffentlich erreichbar.
- Haussprache für Backend ist Python; OIDC über authentik ist im Homelab das etablierte Muster, hier aber aufgeschoben.

Die zentrale Randbedingung ist **bewusst geringe Komplexität**: wenige Bauteile, ein Container, kein externer Dienst.

## Goals / Non-Goals

**Goals:**

- Ein Prozess, ein Container, kein zusätzlicher Dienst (kein Broker, keine separate Datenbank).
- Live-Aktualisierung offener Clients ohne manuelles Neuladen.
- Aufbau so, dass OIDC/authentik später ohne Umbau der Fachlogik ergänzt werden kann.

**Non-Goals:**

- Authentifizierung (kommt als eigener späterer Change).
- Dateien/Bilder, Markdown-Rendering, Bearbeiten bestehender Einträge.
- Mehrere Räume/Boards.
- Horizontale Skalierung oder mehrere Worker.

## Decisions

**1. Stack: FastAPI + Jinja2 + HTMX, serverseitig gerendert.**
Ein Prozess liefert HTML; Interaktion über kleine HTMX-Aufrufe plus etwas JavaScript für SSE und den Kopier-Knopf.
*Alternative:* dasselbe FastAPI+SvelteKit-Doppel wie `vrp` — für diesen Umfang zu schwer (zwei Builds, SPA-Routing). *Alternative:* Go-Einzelbinary — betrieblich noch simpler, aber nicht die Haussprache und ohne den bequemen Authlib-Pfad für später.

**2. Speicher: SQLite als Datei auf einem Volume.**
*Alternative:* die vorhandene Postgres-18-Instanz — bringt einen zweiten Dienst, Migrationen und Netzwerkzugriff, ohne bei dieser Datenmenge Vorteile. Modell ist trivial (`item(id, content, created_at, pinned)`). SQLite im WAL-Modus, Zugriff nur aus dem einen Prozess.

**3. Live-Updates per SSE, nicht WebSocket.**
Die Daten fließen nur Server → Client. `EventSource` verbindet sich selbst neu, ist reines HTTP und braucht keinen Upgrade-Handshake durch die Proxy-Kette. *Alternative:* WebSocket — erst nötig, wenn Clients auch senden (z. B. Tipp-Indikatoren).

**4. Pub/Sub im Prozess (asyncio-Queues), ein Worker.**
Jede schreibende Operation legt den neuen Listenstand in die Queues aller offenen SSE-Streams. Kein Redis, kein Broker. **Bedingung:** genau ein uvicorn-Worker; bei mehreren Workern bräuchte es einen externen Pub/Sub.

**5. Aufräumen bei Zugriff plus leichter Takt.**
`DELETE FROM item WHERE pinned = false AND created_at < now() - TTL` läuft bei jedem Lese-/Schreibzugriff. Zusätzlich läuft prozessintern ein leichter Takt (z. B. alle 60 s), der prüft, ob inzwischen Einträge abgelaufen sind, und dies den offenen Clients mitteilt.
*Grund:* Ohne den Takt würde ein offen liegendes Gerät abgelaufene Einträge erst beim nächsten eigenen Zugriff verlieren und damit die Spec verletzen („abgelaufene Einträge werden nicht mehr angezeigt"). Das ist eine bewusste Verfeinerung der zuvor angedachten reinen Zugriffs-Löschung. Kein Cron, keine separate Schleife im Betrieb, nur ein `asyncio`-Task im selben Prozess.

**6. Obergrenze nur für ungepinnte Einträge.**
`CLIPHOP_MAX_ITEMS` begrenzt die ungepinnten Einträge; beim Überschreiten wird der älteste ungepinnte entfernt. Gepinnte zählen nicht mit und können die Liste nicht sprengen, weil der Nutzer sie aktiv setzt.

**7. Einträge unveränderlich.**
Kein Update-Endpunkt. Ändern heißt löschen und neu ablegen. Eine Änderung ist damit auch in der Live-Übertragung immer ein vollständiger Listenstand.

**8. Deployment wie `vrp`, plus eine SSE-Besonderheit.**
Traefik-Labels für Host `cliphop.rohwer.sh` und `loadbalancer.server.port`. Auf diesem Router **keine** compress- oder buffering-Middleware, damit der `text/event-stream` ungepuffert durchläuft; der Server sendet alle ~20 s ein Heartbeat (`: ping`). Der Kopier-Knopf nutzt die Clipboard-API und funktioniert nur im Secure Context — also genau über die bestehende HTTPS-Kette.

## Risks / Trade-offs

- **Kompressions-/Puffer-Middleware bricht SSE** → auf diesem Router keine solchen Middlewares; Heartbeat; über die volle Kette prüfen.
- **Proxy-Leerlauf-Timeout trennt den Stream** → Heartbeat kürzer als das Timeout; `EventSource` verbindet sich selbst neu und holt beim Verbinden den aktuellen Stand.
- **Ein-Worker-Bedingung** → dokumentiert; solange ein Worker läuft, unkritisch. Mehr Worker erfordern später einen externen Pub/Sub.
- **Keine Auth: jeder im LAN kann lesen und schreiben** → akzeptiert, weil nur im LAN auflösbar; OIDC ist als späterer Change vorgesehen, eine Traefik-BasicAuth-Middleware bliebe ein Zwischenschritt.
- **Gepinnte Einträge wachsen unbegrenzt** → bewusst dem Nutzer überlassen; ein Cap für gepinnte wäre eine spätere Ergänzung.
- **Gleichzeitige Schreibvorgänge** → „letzter Schreiber gewinnt"; Clients erhalten immer den kompletten Listenstand, dadurch entstehen keine Teilzustände.

## Migration Plan

- Kein Bestandssystem betroffen; keine Datenmigration.
- Deployment: Image bauen, Compose-Service mit Volume (`/data`), Env-Variablen und Traefik-Labels ergänzen.
- Rollback: Service entfernen; die SQLite-Datei auf dem Volume bleibt unangetastet.

## Open Questions

- Standardwerte für `CLIPHOP_TTL` (Vorschlag `24h`) und `CLIPHOP_MAX_ITEMS` (Vorschlag `50`).
- Ob zusätzlich ein relativer Zeitstempel je Eintrag angezeigt wird (reine UI-Frage, später entscheidbar).
