# Proposal

## Why

Kurze Textnotizen sollen schnell und reibungslos zwischen eigenen Geräten (Handy, Laptop, Desktop) im Heimnetz ausgetauscht werden können. Bestehende Wege (Chat an sich selbst, E-Mail, Notiz-Apps) sind dafür zu umständlich oder verteilen die Daten über fremde Dienste. `cliphop` wird eine kleine, selbst gehostete Weboberfläche für genau diesen Zweck und läuft im bestehenden Docker-Compose-Stack des Homelabs.

## What Changes

- Neue Web-App `cliphop`, erreichbar unter `https://cliphop.rohwer.sh` über die bestehende Kette Browser → HAProxy (TLS) → Traefik → App.
- **Ein gemeinsamer Slot plus Verlauf**: Der neueste Eintrag ist der aktuelle „Clip"; ältere Einträge stehen darunter im Verlauf.
- Einträge anlegen, einzeln löschen sowie einzeln per Pin vor der automatischen Löschung bewahren.
- **Automatische Löschung per TTL** (konfigurierbar über eine Umgebungsvariable); Pin hebt einen Eintrag davon aus.
- **„Alles leeren" mit Nachfrage**: Dialog mit Auswahl, ob auch gepinnte Einträge gelöscht werden.
- **Live-Aktualisierung**: Offene Geräte zeigen neue, gelöschte oder geänderte Einträge ohne manuelles Neuladen an.
- Inhalt beschränkt auf **reinen Text**; Einträge sind unveränderlich (Ändern heißt löschen und neu ablegen).
- Betrieb als eigener Container mit SQLite auf einem Volume; Authentifizierung wird bewusst **aufgeschoben**, da der Hostname per Split-Horizon-DNS nur im LAN auflöst.

## Capabilities

### New Capabilities

- `notes-exchange`: Erfassen, Anzeigen, Löschen und Pinnen kurzer Textnotizen als gemeinsamer Slot mit Verlauf, inklusive TTL-basierter Aufbewahrung und „alles leeren".
- `live-updates`: Übertragung von Änderungen an offene Clients ohne Neuladen, inklusive Verbindungsaufbau, Heartbeat und Wiederverbindung.

### Modified Capabilities

<!-- Keine: das Projekt hat bislang keine Specs. -->

## Impact

- **Neu:** Anwendungscode (FastAPI + Jinja2 + HTMX), Dockerfile, ein Compose-Service mit Traefik-Labels, SQLite-Datenvolume.
- **Konfiguration:** Umgebungsvariablen `CLIPHOP_TTL`, `CLIPHOP_MAX_ITEMS`, `CLIPHOP_DB`, `BASE_URL`.
- **Infrastruktur:** Nutzung der bestehenden HAProxy-/Traefik-Kette; auf dem SSE-Router dürfen keine Kompressions- oder Puffer-Middlewares aktiv sein.
- **Keine bestehenden Systeme betroffen**: keine vorhandenen Codebasen, Specs oder APIs werden geändert.
- **Aufgeschoben:** OIDC-Anmeldung über authentik. Der Aufbau muss sie später ohne Umbau erlauben, ist aber nicht Teil dieses Changes.
