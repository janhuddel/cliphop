# Design

## Context

Siehe `proposal.md` für die Motivation; die Anforderung steht in `specs/live-updates/spec.md`. Der folgende Text erklärt das *Wie*.

Bestand, auf dem aufgesetzt wird:

- `GET /` rendert die Liste serverseitig über `render_page(store.list_items())`; die Einträge stehen also bereits im gelieferten HTML. Eine wirklich neu geladene Seite kann nicht „leer" sein.
- `src/cliphop/static/app.js` öffnet beim Laden einen `EventSource` auf `/events` und ersetzt bei jeder Nachricht `#list.innerHTML`; der Server schickt beim Verbinden zuerst den aktuellen Stand (`stream_events`).
- Strukturell ist die Liste ein per HTMX und SSE aktualisierter Ausschnitt — der Fix muss also auf dem bestehenden Kanal aufsetzen, nicht einen zweiten Weg zum Server schaffen.
- `GET /` setzt derzeit **kein** `Cache-Control`; nur `/events` hat `cache-control: no-cache` und `x-accel-buffering: no`.

Daraus folgt die beobachtete Ursache: Öffnet man die installierte Web-App, setzt iOS die suspendierte Seite fort (kein Reload). Das stehengebliebene DOM ist der alte Stand, und aktualisiert wird erst, wenn `EventSource` nach dem Aufwachen von selbst neu verbindet — die beobachteten Sekunden Verzögerung.

## Goals / Non-Goals

**Goals:**

- Beim Zurückkehren in den Vordergrund sofort den aktuellen Stand anzeigen, ohne Zutun des Nutzers.
- Keine zwischengespeicherte HTML-Kopie als veralteten Ausgangsstand ausliefern.
- So klein wie möglich: kein neuer Serverweg, keine neue Abhängigkeit, keine Änderung an Endpunkten oder Datenmodell.

**Non-Goals:**

- Kein Service Worker, keine Offline-Fähigkeit (weiterhin der Linie aus `add-ios-home-screen` folgend).
- Kein periodisches Polling und kein sichtbares „Aktualisieren"-Bedienelement.
- Keine Änderung an der SSE-Mechanik oder der Proxy-Kette.

## Decisions

**1. Sofortiger Reconnect bei `visibilitychange`, statt auf den Auto-Reconnect zu warten.**
Der Server liefert beim Verbinden zuerst den aktuellen Stand; ein neuer `EventSource` ist damit der kürzeste Weg zu einer aktuellen Anzeige. Deshalb wird die Aufbaulogik in eine Funktion gezogen und bei `document.visibilityState === "visible"` die bestehende Verbindung geschlossen und sofort neu aufgebaut. *Alternative:* auf den automatischen Reconnect von `EventSource` vertrauen — genau der Zustand, der die mehrsekündige Lücke verursacht. *Alternative:* bei jeder Rückkehr `location.reload()` — einfacher, wirft aber eine halb getippte Eingabe weg und fühlt sich wie ein Neuladen an.

**2. Wiederherstellung aus dem Zwischenspeicher gesondert behandeln.**
Wird die Seite aus dem Back/Forward-Cache (bfcache) zurückgeholt, feuert kein `visibilitychange`, sondern `pageshow` mit `event.persisted === true`; dann ist ein `location.reload()` richtig, weil die Seite samt DOM aus dem Zwischenspeicher kommt. Das ist auf den Fall beschränkt, damit normales Laden kein zusätzliches Neuladen auslöst. *Alternative:* nur `visibilitychange` — deckt die bfcache-Rückkehr nicht ab.

**3. `Cache-Control: no-store` auf `GET /`.**
Ohne Header darf ein Browser die HTML-Seite heuristisch zwischenspeichern und beim Start einen alten Stand zeigen. `no-store` unterbindet das. *Alternative:* `no-cache` — erlaubt Zwischenspeicherung mit Revalidierung, ohne `ETag`/`Last-Modified` aber praktisch nicht besser. *Alternative:* `ETag`/`Last-Modified` — mehr Aufwand für eine dynamische, winzige Seite ohne Nutzen.

**4. Reconnect-Logik an einer Stelle, nicht zwei Event-Handler mit eigener Verbindung.**
`visibilitychange` und `pageshow` teilen sich dieselbe Aufbau-/Schließen-Funktion; mehrfaches Feuern erzeugt so keine parallelen Kanäle.

## Risks / Trade-offs

- **Doppelte oder verwaiste Verbindungen** → Vor dem Neuaufbau die bestehende Verbindung schließen; ohne das sammeln sich Kanäle an.
- **Reconnect bei jedem Sichtbarwerden** → eine Verbindung pro Rückkehr, unkritisch für einen einzelnen Worker; der Server räumt abgebrochene Streams über `request.is_disconnected` auf.
- **`location.reload()` verwirft Eingaben im Textfeld** → nur im bfcache-Fall (`event.persisted`), nicht bei jedem Laden.
- **Fix ist nicht am Gerät verifizierbar** → `no-store` wird automatisiert getestet; das Rückkehr-Verhalten prüft der Nutzer nach dem Deployment am iPhone.
- **iOS könnte das Suspendieren künftig ändern** → dann ist der Fix überflüssig, aber harmlos.

## Migration Plan

- Keine Datenmigration; nur Client-Skript und ein Response-Header.
- Da `static/` im Wheel liegt, ist ein neues Image nötig: Version an den drei Stellen anheben, Image bauen und pushen, Service neu starten.
- Rollback: vorheriges Image starten; Daten und installierte Web-App bleiben unberührt.
