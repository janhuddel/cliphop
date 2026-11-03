# Spec Delta

## Purpose

Erlaubt das Erfassen, Anzeigen, Pinnen und Löschen kurzer Textnotizen als gemeinsamer Slot mit Verlauf, der sich per TTL selbst aufräumt.

## ADDED Requirements

### Requirement: Aktueller Slot und Verlauf
Die Anwendung SHALL gespeicherte Einträge absteigend nach Anlagezeitpunkt anzeigen. Der neueste Eintrag ist der aktuelle Slot, alle älteren bilden darunter den Verlauf.

#### Scenario: Neuester Eintrag ist der Slot
- **WHEN** mehrere Einträge vorhanden sind
- **THEN** steht der zuletzt angelegte Eintrag oben als Slot und die übrigen stehen darunter im Verlauf

#### Scenario: Leerer Zustand
- **WHEN** noch kein Eintrag existiert
- **THEN** zeigt die Anwendung einen leeren Zustand ohne Slot und ohne Verlauf

### Requirement: Eintrag anlegen
Die Anwendung SHALL das Ablegen eines neuen Eintrags mit reinem Text erlauben. Ein neuer Eintrag MUST mit dem aktuellen Zeitpunkt gespeichert werden.

#### Scenario: Neuer Eintrag erscheint oben
- **WHEN** ein Nutzer Text ablegt
- **THEN** wird der Eintrag gespeichert und erscheint als neuester Eintrag oben

#### Scenario: Leerer Text wird abgelehnt
- **WHEN** der abzulegende Text leer ist oder nur aus Leerraum besteht
- **THEN** wird kein Eintrag angelegt und der Nutzer erhält einen Hinweis

#### Scenario: Eingabefeld wird geleert
- **WHEN** ein Nutzer einen Text erfolgreich ablegt
- **THEN** ist das Eingabefeld danach leer; wird der Text abgelehnt, bleibt die Eingabe erhalten

### Requirement: Einträge sind unveränderlich
Ein gespeicherter Eintrag SHALL nach dem Anlegen nicht mehr verändert werden können.

#### Scenario: Kein Bearbeiten eines Eintrags
- **WHEN** ein Nutzer den Inhalt eines bestehenden Eintrags ändern möchte
- **THEN** steht dafür keine Bearbeitungsfunktion bereit; eine Änderung erfordert das Löschen und erneute Anlegen

### Requirement: Eintrag einzeln löschen
Die Anwendung SHALL das Löschen eines einzelnen Eintrags erlauben, unabhängig davon, ob er gepinnt ist.

#### Scenario: Gepinnter Eintrag ist löschbar
- **WHEN** ein Nutzer einen gepinnten Eintrag löscht
- **THEN** verschwindet der Eintrag aus der Liste

### Requirement: Einträge pinnen
Die Anwendung SHALL es erlauben, einzelne Einträge zu pinnen und den Pin wieder zu entfernen. Ein Pin schützt einen Eintrag vor der TTL-Löschung.

#### Scenario: Pin bewahrt vor der TTL
- **WHEN** ein Eintrag gepinnt ist und älter als die TTL wird
- **THEN** bleibt der Eintrag erhalten

#### Scenario: Pin wieder entfernen
- **WHEN** der Pin eines Eintrags entfernt wird
- **THEN** unterliegt der Eintrag wieder der TTL

### Requirement: TTL-basierte Aufbewahrung
Die Anwendung SHALL ungepinnte Einträge entfernen, die älter als die konfigurierte TTL sind. Die TTL MUST über eine Umgebungsvariable einstellbar sein.

#### Scenario: Abgelaufene ungepinnte Einträge verschwinden
- **WHEN** die TTL seit dem Anlegen eines ungepinnten Eintrags überschritten ist
- **THEN** wird der Eintrag nicht mehr angezeigt und nicht mehr gespeichert

#### Scenario: TTL ist konfigurierbar
- **WHEN** die Umgebungsvariable für die TTL geändert und die Anwendung neu gestartet wird
- **THEN** richtet sich die Aufbewahrung nach dem neuen Wert

### Requirement: Obergrenze für ungepinnte Einträge
Die Anwendung SHALL die Anzahl ungepinnter Einträge auf eine konfigurierbare Obergrenze begrenzen. Gepinnte Einträge zählen nicht gegen diese Grenze.

#### Scenario: Ältester ungepinnter Eintrag fällt heraus
- **WHEN** ein neuer Eintrag die Obergrenze ungepinnter Einträge überschreitet
- **THEN** wird der älteste ungepinnte Eintrag entfernt

#### Scenario: Gepinnte Einträge bleiben erhalten
- **WHEN** die Obergrenze überschritten wird und der älteste Eintrag gepinnt ist
- **THEN** bleibt der gepinnte Eintrag erhalten und der älteste ungepinnte Eintrag wird entfernt

### Requirement: Alles leeren mit Nachfrage
Die Anwendung SHALL das Leeren der Liste nur nach Bestätigung in einem Dialog erlauben. Der Dialog MUST wahlweise auch gepinnte Einträge einschließen.

#### Scenario: Nur ungepinnte Einträge leeren
- **WHEN** der Nutzer den Bestätigungsdialog ohne die Option für gepinnte Einträge bestätigt
- **THEN** werden alle ungepinnten Einträge entfernt und gepinnte Einträge bleiben erhalten

#### Scenario: Auch gepinnte Einträge leeren
- **WHEN** der Nutzer im Dialog die Option für gepinnte Einträge aktiviert und bestätigt
- **THEN** werden alle Einträge einschließlich der gepinnten entfernt

#### Scenario: Leeren abbrechen
- **WHEN** der Nutzer den Bestätigungsdialog abbricht
- **THEN** bleibt die Liste unverändert
