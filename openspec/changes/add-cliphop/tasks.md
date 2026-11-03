# Tasks

## 1. Projektgerüst

- [x] 1.1 Projektstruktur und Abhängigkeiten anlegen (FastAPI, Jinja2, uvicorn, pytest, httpx; Python via `uv`) und verifizieren, dass `uv run python -c "import fastapi, jinja2"` fehlerfrei läuft
- [x] 1.2 App-Gerüst mit Health-Endpunkt erstellen und verifizieren, dass `GET /health` `ok` liefert

## 2. Datenmodell und Aufbewahrung

- [x] 2.1 SQLite-Schema `item(id, content, created_at, pinned)` mit WAL-Modus und Zugriffsschicht anlegen und mit einem Unit-Test verifizieren, dass Anlegen und Lesen funktionieren
- [x] 2.2 Einträge anlegen und absteigend nach `created_at` ausliefern; verifizieren, dass leerer/nur aus Leerraum bestehender Text abgelehnt wird und die Reihenfolge stimmt
- [x] 2.3 Pin umschalten und Eintrag einzeln löschen (auch gepinnt) implementieren und mit Tests verifizieren
- [x] 2.4 TTL-Löschung und Obergrenze (`CLIPHOP_MAX_ITEMS`, nur ungepinnte; ältester ungepinnter fällt heraus) implementieren und mit Tests gegen eine feste Uhrzeit verifizieren
- [x] 2.5 „Alles leeren" mit Parameter `include_pinned` implementieren und mit Tests für beide Fälle (nur ungepinnte / auch gepinnte) verifizieren
- [x] 2.6 Konfiguration aus Umgebungsvariablen (`CLIPHOP_TTL` Vorgabe `24h`, `CLIPHOP_MAX_ITEMS` Vorgabe `50`, `CLIPHOP_DB`) mit Vorgabewerten einlesen und mit einem Test für die Dauer-Parsing (`24h`, `30m`) verifizieren sowie die Variablen in der README dokumentieren

## 3. HTTP-Endpunkte und Oberfläche

- [x] 3.1 Die Endpunkte `GET /`, `POST /notes`, `DELETE /notes/{id}`, `PATCH /notes/{id}`, `POST /notes/clear` implementieren und mit API-Tests verifizieren
- [x] 3.2 Jinja2-Template für Slot und Verlauf inklusive Ablegefeld und Aktions-Buttons erstellen und verifizieren, dass die gerenderte Seite die Einträge in der richtigen Reihenfolge enthält
- [x] 3.3 Kopier-Knopf über die Clipboard-API und leeren Zustand (noch keine Einträge) umsetzen und im Browser verifizieren, dass Kopieren den Text in die Zwischenablage legt
- [x] 3.4 Bestätigungsdialog für „Alles leeren" mit Option „auch gepinnte Texte" umsetzen und verifizieren, dass ohne Option nur ungepinnte und mit Option alle Einträge verschwinden
- [x] 3.5 README mit Nutzung, Endpunkten und dem Hinweis zum Secure Context für den Kopier-Knopf schreiben und verifizieren, dass die dort angegebenen Befehle wörtlich funktionieren

## 4. Live-Updates

- [x] 4.1 Pub/Sub im Prozess (Menge von asyncio-Queues) implementieren und mit einem Unit-Test verifizieren, dass ein Schreibvorgang den neuen Listenstand an einen Abonnenten liefert
- [x] 4.2 `GET /events` als SSE-Stream mit Heartbeat (~20 s) implementieren und mit einem Test verifizieren, dass nach dem Verbinden ein Event und im Leerlauf ein Heartbeat ankommen
- [x] 4.3 Frontend-`EventSource` zeichnet die Liste bei Events neu und holt nach Wiederverbindung den aktuellen Stand; mit zwei geöffneten Browsern verifizieren, dass eine Änderung ohne Neuladen erscheint
- [x] 4.4 Den periodischen Prüf-Takt (z. B. alle 60 s) implementieren, der abgelaufene Einträge entfernt und dies den Clients mitteilt, und mit einer kurzen Periode plus festem Zeitbezug verifizieren

## 5. Container und Deployment

- [x] 5.1 Dockerfile mit einem einzigen uvicorn-Worker erstellen und verifizieren, dass der gebaute Container startet und `GET /health` `ok` liefert
- [x] 5.2 Compose-Service mit Datenvolume (`/data`), Env-Variablen und Traefik-Labels (Host `cliphop.rohwer.sh`, `loadbalancer.server.port`, keine compress-/buffering-Middleware) ergänzen und verifizieren, dass der Service startet
- [x] 5.3 Deployment-Doku schreiben: `BASE_URL`, Volume, sowie die SSE-Hinweise für HAProxy/Traefik (keine Kompression/Pufferung, Heartbeat vs. Leerlauf-Timeout) und verifizieren, dass sie alle nötigen Schritte auflistet

## 6. Integration über die Kette

- [ ] 6.1 Über `https://cliphop.rohwer.sh` verifizieren, dass ein auf Gerät A abgelegter Eintrag auf Gerät B ohne Neuladen erscheint und der Kopier-Knopf funktioniert (Secure Context)
- [ ] 6.2 Verifizieren, dass der SSE-Stream über HAProxy und Traefik ungepuffert läuft, der Heartbeat die Verbindung in Ruhephasen offen hält und ein kurzer Verbindungsabbruch automatisch aufgefangen wird

## Workflow follow-up

- Change nach abgeschlossenem Review archivieren.
- Ergebnis nach dem Archivieren prüfen.
