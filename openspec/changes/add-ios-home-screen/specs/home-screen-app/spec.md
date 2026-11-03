# Spec Delta

## Purpose

Macht `cliphop` auf dem iPhone als eigenständige Web-App vom Home-Bildschirm aus startbar, mit eigenem Icon und ohne Browser-Bedienelemente.

## ADDED Requirements

### Requirement: Installation auf dem Home-Bildschirm
Die Anwendung SHALL die für die Installation als Web-App nötigen Angaben bereitstellen: Name, Kurzname, Startadresse, Anzeigemodus und ein rasterbares Icon. Nach dem Hinzufügen zum Home-Bildschirm MUST das Icon den Namen der Anwendung tragen.

#### Scenario: Icon erscheint auf dem Home-Bildschirm
- **WHEN** der Nutzer die Seite in Safari öffnet und „Zum Home-Bildschirm" wählt
- **THEN** erscheint ein Icon mit dem Namen „cliphop" auf dem Home-Bildschirm

#### Scenario: Start über die hinterlegte Startadresse
- **WHEN** die Anwendung installiert ist und vom Home-Bildschirm gestartet wird
- **THEN** öffnet sie die hinterlegte Startadresse und zeigt den aktuellen Slot mit Verlauf

### Requirement: Start ohne Browser-Bedienelemente
Beim Start vom Home-Bildschirm SHALL die Anwendung in einem eigenständigen Fenster ohne Adressleiste und ohne Safari-Navigation erscheinen.

#### Scenario: Kein Browser-Chrome
- **WHEN** der Nutzer das Home-Screen-Icon antippt
- **THEN** öffnet sich die Anwendung ohne Adressleiste und ohne Safari-Navigation

#### Scenario: Alle Funktionen im eigenständigen Fenster
- **WHEN** die Anwendung im eigenständigen Fenster läuft
- **THEN** stehen Ablegen, Pinnen, Löschen, Kopieren und die Live-Aktualisierung unverändert zur Verfügung

### Requirement: Sichere Darstellung an den Geräterändern
Im eigenständigen Fenster SHALL der Inhalt die Safe-Areas von Notch bzw. Dynamic Island sowie die Zone des Home-Indikators respektieren, sodass keine Bedienelemente verdeckt werden.

#### Scenario: Nichts wird überdeckt
- **WHEN** die Anwendung auf einem Gerät mit Notch oder Dynamic Island im eigenständigen Fenster geöffnet ist
- **THEN** sind Kopfbereich und Bedienelemente vollständig sichtbar und nicht von Systemelementen überdeckt
