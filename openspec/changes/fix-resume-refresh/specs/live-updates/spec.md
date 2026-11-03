# Spec Delta

## ADDED Requirements

### Requirement: Aktueller Stand beim Zurückkehren in den Vordergrund
Wurde die Anzeige eines Clients zwischenzeitlich angehalten — weil die installierte Web-App im Hintergrund lag, in den Vordergrund zurückkehrt oder aus einem Zwischenspeicher wiederhergestellt wird — SHALL der Client unmittelbar den aktuellen Stand der Einträge zeigen, ohne Zutun des Nutzers und ohne spürbare Verzögerung durch einen erst später nachgeholten Verbindungsaufbau.

#### Scenario: Zurückgekehrte Web-App zeigt sofort den aktuellen Stand
- **WHEN** die installierte Web-App aus dem Hintergrund wieder in den Vordergrund kommt und ihre Anzeige noch einen älteren Stand enthält
- **THEN** zeigt sie den aktuellen Stand der Einträge, ohne dass der Nutzer etwas tun muss

#### Scenario: Zwischenzeitlich abgelegter Eintrag ist sofort sichtbar
- **WHEN** ein Eintrag abgelegt wurde, während die App nicht im Vordergrund war, und die App danach geöffnet wird
- **THEN** erscheint dieser Eintrag sofort in der Anzeige

#### Scenario: Kein veralteter Stand aus dem Zwischenspeicher
- **WHEN** die Seite aus einem Zwischenspeicher wiederhergestellt wird und der gespeicherte Stand nicht mehr aktuell ist
- **THEN** wird der aktuelle Stand angezeigt und nicht der zwischengespeicherte
