# Tasks

## 1. Icons und Manifest

- [x] 1.1 Aus dem vorhandenen Motiv `src/cliphop/static/favicon.svg` die PNG-Icons `icon-180.png` (apple-touch-icon) und `icon-512.png` (Manifest) rastern und verifizieren, dass beide Dateien existieren und die Maße 180x180 bzw. 512x512 haben (z. B. `file` oder Pillow)
- [x] 1.2 `src/cliphop/static/manifest.webmanifest` mit `name`, `short_name`, `start_url: "/"`, `scope: "/"`, `display: "standalone"`, `theme_color`, `background_color` und den Icon-Einträgen anlegen und mit einem API-Test verifizieren, dass `GET /static/manifest.webmanifest` mit 200 antwortet und gültiges JSON mit `scope: "/"` und `display: "standalone"` liefert

## 2. HTML-Kopf und Standalone-Darstellung

- [x] 2.1 In `src/cliphop/templates/index.html` den Manifest-Link, `apple-touch-icon`, `theme-color`, `apple-mobile-web-app-capable` und `apple-mobile-web-app-status-bar-style` ergänzen und mit einem Test verifizieren, dass die von `GET /` gelieferte Seite diese Angaben enthält
- [x] 2.2 `viewport-fit=cover` im Viewport-Meta setzen und in `src/cliphop/static/style.css` die Abstände um `env(safe-area-inset-*)` ergänzen und verifizieren, dass das gerenderte `viewport`-Meta `viewport-fit=cover` enthält und der Kopfbereich auf einem Gerät mit Notch/Dynamic Island nicht überdeckt wird

## 3. Kurzbefehl für das Teilen-Menü (Doku)

- [x] 3.1 `docs/SHORTCUTS.md` mit der Schritt-für-Schritt-Einrichtung des iOS-Kurzbefehls schreiben (Eingabe „Text“ aus dem Teilen-Menü, `POST https://cliphop.rohwer.sh/notes` mit Formfeld `content`, Teilen-Menü aktivieren, Hinweis zur LAN-Abhängigkeit) und verifizieren, dass der dokumentierte Aufruf wörtlich funktioniert (`curl --data-urlencode "content=..." https://cliphop.rohwer.sh/notes` legt einen Eintrag an)
- [x] 3.2 In `README.md` auf `docs/SHORTCUTS.md` verweisen und verifizieren, dass der Verweis auf eine existierende Datei zeigt

## 4. Deployment und Prüfung auf dem Gerät

- [x] 4.1 Die Version an den drei Stellen (`pyproject.toml`, Dockerfile `ARG VERSION`, `compose.yaml`-Tag) anheben, Image bauen und pushen, Service neu starten und verifizieren, dass der Container gesund ist und `https://cliphop.rohwer.sh/static/manifest.webmanifest` ausgeliefert wird
- [x] 4.2 Die Web-App auf dem iPhone über Safari → „Zum Home-Bildschirm" installieren und verifizieren, dass ein Icon mit dem Namen „cliphop" erscheint und der Start darüber ohne Adressleiste die Seite mit Slot und Verlauf öffnet
- [x] 4.3 Im eigenständigen Fenster Ablegen, Pinnen, Löschen und Kopieren ausführen und mit zwei Geräten verifizieren, dass eine Änderung im jeweils anderen Fenster ohne Neuladen erscheint
- [x] 4.4 Den Kurzbefehl aus `docs/SHORTCUTS.md` einrichten und verifizieren, dass markierter Text aus einer anderen App über das Teilen-Menü abgelegt und im geöffneten Fenster ohne Neuladen sichtbar wird

## Workflow follow-up

- Change nach abgeschlossenem Review archivieren.
- Ergebnis nach dem Archivieren prüfen.
