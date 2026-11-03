# cliphop

Kurze Textnotizen schnell zwischen eigenen Geräten austauschen. Der neueste
Eintrag ist der „aktuelle" Slot, alles darunter der Verlauf. Läuft im Homelab
in einem Container hinter HAProxy → Traefik.

## Endpunkte

| Methode | Pfad           | Zweck                                        |
|---------|----------------|----------------------------------------------|
| GET     | `/`            | Seite mit Slot und Verlauf                   |
| GET     | `/health`      | Lebenszeichen (`ok`)                          |
| POST    | `/notes`       | Eintrag ablegen (Formfeld `content`)          |
| DELETE  | `/notes/{id}`  | Eintrag löschen                              |
| PATCH   | `/notes/{id}`  | Pin umschalten                                |
| POST    | `/notes/clear` | Liste leeren; Feld `include_pinned` optional  |
| GET     | `/events`      | SSE-Stream für Live-Aktualisierung            |

## Konfiguration

| Variable                 | Vorgabe                       | Zweck                                        |
|--------------------------|-------------------------------|----------------------------------------------|
| `CLIPHOP_TTL`            | `24h`                         | Lebensdauer ungepinnter Einträge (`30m`, `7d`) |
| `CLIPHOP_MAX_ITEMS`      | `50`                          | Obergrenze ungepinnter Einträge              |
| `CLIPHOP_DB`             | `/data/cliphop.db`            | Pfad der SQLite-Datei                         |
| `BASE_URL`               | `https://cliphop.rohwer.sh`   | Öffentliche Adresse (spätere Auth/Links)      |
| `CLIPHOP_SSE_HEARTBEAT`  | `20`                          | Sekunden zwischen Lebenszeichen im SSE-Stream |
| `CLIPHOP_PRUNE_INTERVAL` | `60`                          | Sekunden zwischen dem Prüf-Takt               |

## Betrieb mit Docker

Der Service läuft als einzelner Container mit **einem** Worker und legt die
SQLite-Datei auf ein Volume. Beispiel siehe [`compose.yaml`](compose.yaml);
Details zur Proxy-Kette in [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

```sh
docker build -t cliphop .
docker run --rm -p 8000:8000 -v cliphop-data:/data cliphop
curl http://localhost:8000/health   # -> ok
```

## Entwicklung

```sh
uv sync
CLIPHOP_DB=./data/cliphop.db uv run uvicorn cliphop.app:create_app --factory --reload
uv run pytest
```

Lokal ohne Docker: `CLIPHOP_DB` auf einen beschreibbaren Pfad setzen (die
Vorgabe `/data/…` existiert außerhalb des Containers nicht).

## Kurzbefehl am iPhone

Markierten Text aus jeder App direkt ablegen: Die Schritt-für-Schritt-
Einrichtung eines iOS-Kurzbefehls für das Teilen-Menü steht in
[`docs/SHORTCUTS.md`](docs/SHORTCUTS.md).

## Hinweis zum Kopier-Knopf

Der Knopf nutzt die Clipboard-API des Browsers. Die funktioniert nur im
**Secure Context**, also über `https://` oder `localhost`. Über die bestehende
HTTPS-Kette ist das erfüllt; bei reinem `http://` greift ein Rückfall ohne
direkte Zwischenablage.
