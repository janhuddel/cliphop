# Design

## Context

Siehe `proposal.md` für Motivation und Umfang; die Anforderungen stehen in `specs/home-screen-app/spec.md`. Der folgende Text erklärt das *Wie*.

Bestand, auf dem aufgesetzt wird:

- `src/cliphop/static/` wird per `StaticFiles` unter `/static` ausgeliefert und über `hatchling` in das Wheel gepackt — statische Änderungen brauchen also ein neues Image, nicht nur einen Neustart.
- `src/cliphop/templates/index.html` setzt bereits `viewport` und ein SVG-Favicon; ein Manifest oder Home-Screen-Icon fehlt.
- `GET /` ist die einzige Seite; sie liefert Slot und Verlauf, Live-Updates laufen über `GET /events`.
- Die Kette liefert HTTPS, also den für PWA und Clipboard nötigen Secure Context.
- Kein Authentifizierungsschritt vorhanden; der Hostname löst per Split-Horizon nur im LAN auf.

## Goals / Non-Goals

**Goals:**

- Die Seite als Web-App installierbar machen, die vom Home-Bildschirm in einem eigenständigen Fenster startet.
- Das Layout im eigenständigen Fenster von Notch/Dynamic Island und Home-Indikator freihalten.
- Den „schnell Text ablegen"-Weg über das iOS-Teilen-Menü als Doku bereitstellen, ohne den Endpunkt anzufassen.

**Non-Goals:**

- Kein Service Worker, keine Offline-Fähigkeit, kein Push.
- Kein Installations-Hinweis in der Oberfläche.
- Keine Änderung an Endpunkten, Datenmodell, Konfiguration oder Container.
- Keine Authentifizierung und keine öffentliche Erreichbarkeit (späterer Change).

## Decisions

**1. Manifest als Datei unter `static/`, aber mit explizitem `scope: "/"`.**
`StaticFiles` liefert aus `/static/`; ohne Scope-Angabe fiele der Installations-Scope auf `/static/` und der Start vom Icon würde nicht auf `/` landen. Deshalb `"scope": "/"` und `"start_url": "/"` im Manifest. *Alternative:* eine eigene Route `/manifest.webmanifest` in `app.py` — derselbe Effekt, aber zusätzlicher Code ohne Mehrwert. *Verworfen:* das Manifest über eine Route dynamisch bauen, weil sich nichts zur Laufzeit ändert.

**2. Icons einmalig aus `favicon.svg` rastern, PNG committen.**
iOS nutzt für den Home-Bildschirm `apple-touch-icon` und skaliert SVG nicht zuverlässig; ohne PNG zieht iOS einen Screenshot der Seite heran. Aus dem vorhandenen Motiv (grüne Kachel, drei abnehmende Balken) entstehen `icon-180.png` (apple-touch-icon) und `icon-512.png` (Manifest). Das Rastern ist ein einmaliger Schritt; die PNGs liegen im Repo. *Alternative:* SVG im Manifest — für iOS unzuverlässig.

**3. Standalone über Manifest-`display`, das alte Meta nur als Beigabe.**
Ab iOS 16.4 entscheidet das Manifest über den Anzeigemodus; `"display": "standalone"` ist damit maßgeblich. `apple-mobile-web-app-capable` wird trotzdem gesetzt: klein, unschädlich, hilft älteren Geräten. *Alternative:* nur das Meta — auf heutigen Geräten nicht mehr der richtige Weg.

**4. Safe-Areas statt durchsichtiger Statusleiste.**
`viewport-fit=cover` plus `env(safe-area-inset-*)` in den bestehenden Abständen; Statusleistenstil bleibt `default`. Damit reserviert iOS Platz für die Statusleiste, und die Insets fangen die Notch im Querformat sowie den Home-Indikator unten ab. *Alternative:* `black-translucent` für ein randloses Bild — schöner, aber man muss den Inhalt selbst vollständig unter der Statusleiste wegpolstern; mehr Feinschliff und mehr Risiko für genau das in der Spec verbotene Überdecken.

**5. Kein Service Worker in diesem Schritt.**
Die App ist weiterhin nur im LAN erreichbar; Offline ist kein Versprechen dieser Ausbaustufe. Ein SW in einer HTMX-plus-SSE-App ist zudem eine bekannte Cache-Fehlerquelle und müsste `/events` und `/notes` strikt aussparen. *Alternative:* minimaler SW nur für eine Offline-Karte — bewusst auf den öffentlichen Ausbau verschoben.

**6. Teilen-Menü-Kurzbefehl als Doku, nicht als Code.**
`POST /notes` nimmt bereits `application/x-www-form-urlencoded` mit Feld `content` an; „Get Contents of URL" im Kurzbefehl (Body: Form) trifft das ohne Backend-Änderung. Das Rezept kommt in eine eigene Seite `docs/SHORTCUTS.md`, damit die `README.md` knapp bleibt. *Alternative:* ein JSON-Endpunkt für den Kurzbefehl — fürs Schreiben unnötig. *Verworfen für jetzt:* ein Endpunkt zum *Lesen* des aktuellen Slots; er wäre nur für einen lesenden Kurzbefehl nötig und gehört in einen eigenen Change.

**7. Installations-Hinweis nicht in diesem Schritt.**
iOS zeigt keinen Install-Prompt; ein dezenter Hinweis („Zum Home-Bildschirm hinzufügen", nur außerhalb des Standalone-Modus sichtbar) ist Kür und wird aufgeschoben.

## Risks / Trade-offs

- **Falscher Manifest-Scope → Start greift ins Leere** → `scope: "/"` explizit setzen und die Installation auf dem Gerät prüfen (nicht nur das Manifest lesen).
- **iOS cached Manifest und Icons hartnäckig** → Icon- und Namensänderungen wirken erst nach Löschen und erneutem Hinzufügen der Web-App; beim Verifizieren bewusst so vorgehen.
- **Getrenntes Storage-Jar der PWA** → Die installierte Web-App hat ein eigenes Cookie-/Storage-Jar, unabhängig von Safari. Ohne Auth heute unkritisch, aber beim späteren OIDC-Change bedeutet es einen vom Safari-Login getrennten Anmeldevorgang.
- **SSE im Hintergrund** → iOS suspendiert die Web-App; `EventSource` verbindet sich beim Zurückkehren selbst neu und holt den aktuellen Stand. Das deckt `live-updates` bereits ab; kein Handlungsbedarf, aber beim Testen beobachten.
- **LAN-only: Icon öffnet außer Haus ins Leere** → bewusst akzeptiert; Offline-Karte oder öffentlicher Zugang sind spätere Ausbaustufen. Der Kurzbefehl scheitert außerhalb des LANs mit demselben Effekt und wird in der Doku erwähnt.
- **Kein sichtbarer Install-Hinweis** → Nutzer muss den Weg über das Safari-Teilen-Menü kennen; die Kurzbefehl-Doku beschreibt die Einrichtungsschritte und kann den Hinweis mit aufnehmen.

## Migration Plan

- Keine Datenmigration; nur neue statische Dateien sowie Templates- und CSS-Anpassungen.
- Da `static/` und `templates/` über das Wheel ausgeliefert werden, ist ein neues Image nötig (kein reiner Neustart): Version an den drei Stellen anpassen, Image bauen und pushen, Service neu starten.
- Rollback: vorheriges Image starten; die SQLite-Datei und die installierte Web-App bleiben unberührt (letztere ggf. auf dem Gerät entfernen).

## Open Questions

- Ob im öffentlichen Ausbau ein Installations-Hinweis in der App und eine Offline-Karte per Service Worker dazukommen.
- Ob ein lesender Kurzbefehl (aktueller Slot) gewünscht ist — er bräuchte einen eigenen JSON-Endpunkt und damit einen eigenen Change.
