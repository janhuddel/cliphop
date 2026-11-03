# Tasks

## 1. Sofortige Aktualisierung im Client

- [x] 1.1 In `src/cliphop/static/app.js` die Aufbaulogik des Kanals in eine Funktion ziehen und bei `visibilitychange` (Zustand sichtbar) die bestehende Verbindung schließen und sofort neu aufbauen und verifizieren, dass ein Sichtbarwerden im Browser genau eine `/events`-Verbindung erzeugt und keine zweite daneben bestehen bleibt
- [x] 1.2 Einen `pageshow`-Handler ergänzen, der nur bei `event.persisted === true` neu lädt, und verifizieren, dass ein normales Laden der Seite kein zusätzliches Neuladen auslöst

## 2. Kein veralteter HTML-Stand aus dem Zwischenspeicher

- [x] 2.1 `GET /` in `src/cliphop/app.py` mit `Cache-Control: no-store` ausliefern und mit einem API-Test in `tests/test_api.py` verifizieren, dass die Antwort den Header `cache-control: no-store` trägt

## 3. Auslieferung und Prüfung am Gerät

- [x] 3.1 Die Version an den drei Stellen (`pyproject.toml`, Dockerfile `ARG VERSION`, `compose.yaml`-Tag) anheben, Image bauen und pushen, Service neu starten und verifizieren, dass der Container gesund ist und `GET /` die Liste weiterhin samt `Cache-Control: no-store` liefert
- [x] 3.2 Auf dem iPhone die installierte Web-App vollständig schließen, per Kurzbefehl einen Eintrag ablegen, die App öffnen und verifizieren, dass der neue Eintrag unmittelbar erscheint und nicht erst nach einigen Sekunden
- [x] 3.3 Auf dem iPhone verifizieren, dass ein zwischenzeitlicher App-Wechsel zurück zur Web-App den aktuellen Stand zeigt, ohne die Eingabe im Textfeld zu verlieren

## Workflow follow-up

- Change nach abgeschlossenem Review archivieren.
- Ergebnis nach dem Archivieren prüfen.
