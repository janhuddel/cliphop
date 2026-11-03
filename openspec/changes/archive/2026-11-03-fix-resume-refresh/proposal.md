# Proposal

## Why

Die auf dem Home-Bildschirm installierte Web-App wird von iOS suspendiert und beim Öffnen als zuletzt lebende Seite fortgesetzt, also nicht jedes Mal neu geladen. Deshalb steht kurz der alte Stand im Fenster — häufig noch die leere Liste — und erst wenn die SSE-Verbindung nach dem Aufwachen neu aufgebaut ist (mehrere Sekunden), erscheint der aktuelle Inhalt. Wer Text per Kurzbefehl abgelegt hat und danach die App öffnet, sieht zuerst eine leere Liste, obwohl bereits Einträge vorhanden sind. Die bisherige Planung hat das als „kein Handlungsbedarf" abgetan (siehe `design.md` von `add-ios-home-screen`); dieser Change korrigiert das.

## What Changes

- Beim Zurückkehren in den Vordergrund (Web-App-Icon, App-Wechsel, Tab wird wieder sichtbar) baut der Client den Änderungskanal **sofort** neu auf, statt auf den trägen automatischen Reconnect zu warten. Der Server schickt beim Verbinden den aktuellen Stand; der erscheint damit unmittelbar.
- Wird die Seite aus dem Back/Forward-Cache wiederhergestellt, lädt der Client sie neu, damit kein zwischengespeichertes DOM stehen bleibt.
- Die Seite `GET /` wird mit `Cache-Control: no-store` ausgeliefert, damit eine zwischengespeicherte HTML-Kopie nicht einen alten Stand zeigt.
- Unverändert bleiben: der SSE-Mechanismus selbst, alle Endpunkte, das Datenmodell und die Proxy-Kette.

## Capabilities

### New Capabilities

<!-- Keine: Es kommt keine neue Fähigkeit hinzu, die Aktualität der Anzeige gehört zu live-updates. -->

### Modified Capabilities

- `live-updates`: Neue Anforderung, dass ein Client beim Zurückkehren in den Vordergrund den aktuellen Stand unmittelbar zeigt, statt erst nach dem automatischen Reconnect.

## Impact

- **Geändert:** `src/cliphop/static/app.js` (Reconnect bei `visibilitychange`, Reload bei wiederhergestellter Seite), `src/cliphop/app.py` (`Cache-Control: no-store` auf der Seite), `tests/test_api.py`.
- **Unverändert:** Endpunkte, Datenmodell, Konfiguration, Abhängigkeiten, Container, HAProxy/Traefik-Kette.
- **Betrieb:** Da `static/` und `templates/` im Wheel liegen, braucht es ein neues Image: Version an den drei Stellen anheben, Image bauen und pushen, Service neu starten.
