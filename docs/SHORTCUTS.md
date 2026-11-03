# Kurzbefehl: Text aus dem Teilen-Menü ablegen

Mit einem iOS-Kurzbefehl lässt sich markierter Text aus jeder App direkt an
`cliphop` schicken — ohne die App zu wechseln. Der Kurzbefehl nutzt den
bestehenden Endpunkt `POST /notes` (Formfeld `content`); am Server ist nichts
einzurichten.

## Voraussetzungen

- Das iPhone ist im **Heimnetz** (derselbe LAN, in dem `cliphop.rohwer.sh`
  auflöst). Der Hostname ist per Split-Horizon-DNS nur dort erreichbar; außer
  Haus schlägt der Kurzbefehl fehl.
- Die Seite öffnet sich einmal in Safari als Gegenprobe: `https://cliphop.rohwer.sh`.

## Auf dem Home-Bildschirm installieren

`cliphop` braucht keine App aus dem App Store: Safari legt die Seite als
Verknüpfung auf den Home-Bildschirm, und von dort startet sie in einem
eigenständigen Fenster ohne Adressleiste. Einmalig am iPhone:

1. In **Safari** die Seite öffnen: `https://cliphop.rohwer.sh`.
2. Unten in der Symbolleiste das **Teilen**-Symbol antippen (Viereck mit Pfeil
   nach oben).
3. In der Liste **„Zum Home-Bildschirm"** wählen (ggf. etwas nach unten
   scrollen).
4. Den vorbelegten Namen **„cliphop"** übernehmen und **„Hinzufügen"** tippen.

Das Icon erscheint auf dem Home-Bildschirm; ein Tipp darauf öffnet denselben
Slot mit Verlauf, aber ohne Safari-Bedienelemente. Live-Aktualisierung,
Ablegen, Pinnen, Löschen und Kopieren funktionieren dort unverändert.

Hinweis: iOS merkt sich Icon und Name hartnäckig. Nach einer Änderung daran
wirkt sie erst, wenn die Verknüpfung vom Home-Bildschirm gelöscht und neu
angelegt wird.

## Kurzbefehl einrichten

1. **Kurzbefehl anlegen:** In der „Kurzbefehle"-App oben rechts **+** wählen.
2. **Im Teilen-Menü anzeigen:** Auf **ⓘ** (Details) tippen und „**Im Teilen-Menü
   anzeigen**" (je nach iOS-Version „Im Share-Sheet anzeigen") einschalten.
   Unter **Teilen-Menü-Typen** **Text** wählen — und zusätzlich **Rich Text**,
   wenn du auch Notizen aus der Notizen-App ablegen willst (siehe unten). Unter
   „Wenn keine Eingabe" **Weiter** einstellen.
   Am Anfang des Kurzbefehls steht danach automatisch die **Kurzbefehl-Eingabe**.
   Sie ist *keine* Aktion zum Hinzufügen, sondern eine **Variable**, die aus dem
   Teilen-Menü gefüllt wird.
3. **Absenden:** Aktion „**Inhalte von URL abrufen**" (Get Contents of URL)
   hinzufügen und einstellen:
   - **URL:** `https://cliphop.rohwer.sh/notes`
   - **Methode:** `POST`
   - **Anfrage-Body:** `Formular` (Form)
   - **Feld:** Name `content`, Wert = **Kurzbefehl-Eingabe**: ins Wertfeld
     tippen und in der Variablen-Auswahl **Kurzbefehl-Eingabe** wählen (nicht
     den Text eintippen).
4. **Benennen:** Kurzbefehl z. B. „An cliphop senden" nennen.
5. **Ausprobieren:** In einer App Text markieren → **Teilen** → den Kurzbefehl
   wählen. Der Text erscheint als neuer, aktueller Slot; bereits geöffnete
   Fenster aktualisieren sich per Live-Stream ohne Neuladen.

### Kein leeres Eingabefeld

Fragt der Kurzbefehl beim Start nach einem Text und zeigt ein **leeres Feld**,
steckt meist eine Aktion „**Nach Eingabe fragen**" (Ask for Input) oder ein
leeres „Text"-Feld im Kurzbefehl — dann ist die Teilen-Eingabe nicht verdrahtet.
So behebst du das:

- Die Aktion „Nach Eingabe fragen" bzw. das leere Text-Feld **löschen**.
- Im Feld `content` den Wert über die **Variablen-Auswahl** auf
  **Kurzbefehl-Eingabe** setzen.
- Prüfen, dass „Im Teilen-Menü anzeigen" **an** ist.

Wird der Kurzbefehl direkt aus der App (ohne Teilen) gestartet, kommt keine
Eingabe an; dann antwortet der Server mit „Bitte zuerst einen Text eingeben."
Das ist erwartet — Text erreicht den Kurzbefehl nur über das Teilen-Menü.

## Notiz aus der Notizen-App ablegen

Eine **geöffnete** Notiz wird **nicht** automatisch übernommen: iOS gibt nur
weiter, was die App über **Teilen** herausgibt, und das Empfangen von
Bildschirmobjekten („Bildschirmobjekte empfangen") unterstützt nur bestimmte
Apps (Safari, Karten, Fotos …) — die Notizen-App ist nicht dabei.

- **Mit Teilen:** Notiz öffnen → **Teilen** → Kurzbefehl. „Notizen" teilt
  formatierte Inhalte, deshalb muss der Kurzbefehl zusätzlich **Rich Text** als
  Teilen-Typ akzeptieren (siehe oben). Enthält die Notiz Anhänge, teilt iOS sie
  womöglich als PDF — dann funktioniert es nicht.
- **Über die Zwischenablage (ohne Teilen):** In „Notizen" den Text kopieren
  („Kopieren"), dann den Kurzbefehl über Home-Bildschirm, Back-Tap oder Suche
  starten. Dafür im Kurzbefehl als Wert für `content` statt der
  Kurzbefehl-Eingabe die Aktion „**Zwischenablage abrufen**" (Get Clipboard)
  einsetzen — am saubersten in einem zweiten Kurzbefehl.

## Gegenprobe per Terminal

Derselbe Aufruf von einem Rechner im Heimnetz muss einen Eintrag anlegen:

```sh
curl --data-urlencode "content=Hallo von curl" https://cliphop.rohwer.sh/notes
```

Antwort ist der neu gerenderte Listen-Ausschnitt mit dem eben abgelegten Text.
Anschließend erscheint der Eintrag auch in der geöffneten Seite.
