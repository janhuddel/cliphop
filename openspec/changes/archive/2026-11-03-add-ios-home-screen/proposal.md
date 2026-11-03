# Proposal

## Why

`cliphop` wird vor allem am iPhone benutzt, aber jeder Zugriff beginnt heute in Safari mit Adressleiste und manuellem Aufruf. iOS kann eine Web-App ohne native App auf den Home-Bildschirm legen und in einem eigenen Fenster starten — dafür fehlen der App nur Manifest, Icon und die passenden Metas. Zusätzlich ist der häufigste Anwendungsfall „Text aus einer anderen App schnell ablegen"; ein Kurzbefehl im Teilen-Menü erspart dafür den App-Wechsel vollständig.

Beides ist reine Auslieferungs- und Oberflächenarbeit: Die bestehenden Endpunkte, insbesondere `POST /notes` mit Formfeld `content`, bleiben unverändert. Der Schritt bleibt bewusst **LAN-only**; Authentifizierung und öffentliche Erreichbarkeit sind ein separater, späterer Change.

## What Changes

- **Installierbare Web-App (PWA)**: Web-App-Manifest mit `display: standalone` und `scope: "/"`, PNG-Icons für den Home-Bildschirm, Verknüpfung im HTML-Kopf sowie `theme-color`.
- **Standalone-Darstellung auf iOS**: Der Start vom Home-Bildschirm erfolgt ohne Safari-Adressleiste; das Layout berücksichtigt die Safe-Areas von Notch/Dynamic Island.
- **Kurzbefehl-Rezept für das Teilen-Menü**: dokumentierte Einrichtung eines iOS-Kurzbefehls, der markierten Text per `POST /notes` ablegt. Kein Code, nur Doku — der Endpunkt kann das bereits.
- **Kein Service Worker in diesem Schritt**: Da die App weiterhin nur im LAN erreichbar ist, wird keine Offline-Fähigkeit versprochen; eine Offline-Karte ist bewusst aufgeschoben.
- **Nicht enthalten**: Authentifizierung, öffentliche Erreichbarkeit, Push-Benachrichtigungen, Offline-Caching, ein Installations-Prompt in der App.

## Capabilities

### New Capabilities

- `home-screen-app`: Die Anwendung lässt sich auf dem Home-Bildschirm installieren und startet dort als eigenständiges Fenster mit eigenem Icon und Namen, ohne Browser-Bedienelemente.

### Modified Capabilities

<!-- Keine: Manifest, Icons und Safe-Areas ändern die Darstellung, nicht das Verhalten der bestehenden Fähigkeiten. Der Kurzbefehl nutzt den bereits spezifizierten Endpunkt POST /notes. -->

## Impact

- **Neu:** `src/cliphop/static/manifest.webmanifest`, `src/cliphop/static/icon-180.png`, `src/cliphop/static/icon-512.png`, eine Doku-Seite für den Kurzbefehl (z. B. `docs/SHORTCUTS.md`).
- **Geändert:** `src/cliphop/templates/index.html` (Manifest-, Icon- und Theme-Verknüpfung), `src/cliphop/static/style.css` (Safe-Area-Insets), ggf. `README.md` (Verweis auf die Kurzbefehl-Doku).
- **Unverändert:** alle HTTP-Endpunkte, Datenmodell, Konfiguration, Abhängigkeiten, Container und Deployment.
- **Betrieb:** keine neue Middleware, kein zusätzlicher Dienst; die bestehende HTTPS-Kette liefert bereits den für PWA und Clipboard nötigen Secure Context.
