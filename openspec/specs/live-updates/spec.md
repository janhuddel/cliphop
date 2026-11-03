# live-updates Specification

## Purpose

Hält alle geöffneten Clients ohne manuelles Neuladen auf demselben Stand, sobald sich die Einträge ändern.

## Requirements

### Requirement: Änderungen werden an offene Clients übertragen
Die Anwendung SHALL jede Änderung an den Einträgen an alle offenen Clients übertragen, damit diese ihre Anzeige ohne Neuladen aktualisieren.

#### Scenario: Neuer Eintrag erscheint auf einem anderen Gerät
- **WHEN** auf einem Gerät ein Eintrag angelegt wird
- **THEN** nimmt ein anderes geöffnetes Gerät den Eintrag ohne Neuladen in seine Anzeige auf

#### Scenario: Löschung erscheint auf einem anderen Gerät
- **WHEN** ein Eintrag gelöscht wird
- **THEN** entfernt ein anderes geöffnetes Gerät den Eintrag ohne Neuladen aus seiner Anzeige

#### Scenario: Pin-Änderung erscheint auf einem anderen Gerät
- **WHEN** der Pin eines Eintrags umgeschaltet wird
- **THEN** zeigt ein anderes geöffnetes Gerät den geänderten Pin-Zustand ohne Neuladen

### Requirement: Verbindungsaufbau ohne zusätzliche Einrichtung
Die Anwendung SHALL es einem Client erlauben, beim Öffnen der Seite einen dauerhaften Kanal für Änderungen aufzubauen, ohne dass dafür eine gesonderte Einrichtung nötig ist.

#### Scenario: Kanal nach dem Öffnen der Seite
- **WHEN** ein Client die Seite öffnet
- **THEN** baut er den Kanal auf und empfängt nachfolgende Änderungen

### Requirement: Lebenszeichen bei Leerlauf
Die Anwendung SHALL in Phasen ohne Änderungen regelmäßig ein Lebenszeichen senden, damit die Verbindung über die Proxy-Kette bestehen bleibt.

#### Scenario: Verbindung überlebt eine ruhige Phase
- **WHEN** längere Zeit keine Änderung anfällt
- **THEN** bleibt die Verbindung bestehen, weil die Anwendung Lebenszeichen sendet

### Requirement: Aktueller Stand nach Wiederverbindung
Die Anwendung SHALL einen Client nach einem Verbindungsabbruch wieder auf den aktuellen Stand bringen.

#### Scenario: Client holt nach Abbruch den neuesten Stand
- **WHEN** die Verbindung unterbrochen war und sich der Client erneut verbindet
- **THEN** zeigt er die aktuellste Liste

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
