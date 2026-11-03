# Deployment

`cliphop` läuft als ein Container im bestehenden Docker-Compose-Stack des
Homelabs, hinter der Kette **Browser → HAProxy (TLS) → Traefik → App**.
Der Hostname `cliphop.rohwer.sh` löst per Split-Horizon-DNS nur im LAN auf.

## Schritte

1. Image bauen und in die Registry schieben:

   ```sh
   docker build --build-arg VERSION=1.0.0 -t oci.rohwer.sh/cliphop:1.0.0 .
   docker push oci.rohwer.sh/cliphop:1.0.0
   ```

   Die Version steht in `pyproject.toml`, wird beim Bauen als
   `org.opencontainers.image.version` ins Image geschrieben und im Compose-
   Service als Tag verwendet — beim Versionssprung alle drei Stellen anpassen.

2. Den Service aus [`compose.yaml`](../compose.yaml) in den bestehenden Stack
   übernehmen und starten.

3. Prüfen, dass der Container gesund ist:

   ```sh
   curl http://<container-host>:8000/health   # -> ok
   ```

## Konfiguration

| Variable                 | Vorgabe                       | Zweck                                        |
|--------------------------|-------------------------------|----------------------------------------------|
| `CLIPHOP_TTL`            | `24h`                         | Lebensdauer ungepinnter Einträge             |
| `CLIPHOP_MAX_ITEMS`      | `50`                          | Obergrenze ungepinnter Einträge              |
| `CLIPHOP_DB`             | `/data/cliphop.db`            | Pfad der SQLite-Datei                        |
| `BASE_URL`               | `https://cliphop.rohwer.sh`   | Öffentliche Adresse                          |
| `CLIPHOP_SSE_HEARTBEAT`  | `20`                          | Sekunden zwischen Lebenszeichen im SSE-Stream |
| `CLIPHOP_PRUNE_INTERVAL` | `60`                          | Sekunden zwischen dem Prüf-Takt               |

`BASE_URL` wird heute nicht für die Adressbildung gebraucht (alle Pfade sind
relativ). Sie steht bereit, sobald Authentifizierung dazukommt.

## Volume und Backup

Die SQLite-Datei liegt auf dem Volume `cliphop-data` unter `/data`. Das ist ein
**lokales** Docker-Volume und bewusst **kein NFS-Mount**: SQLite braucht
zuverlässige Dateilocks, und der WAL-Modus zusätzlich funktionierendes
Shared-Memory-`mmap` — beides ist über NFS unsicher. Der NFS-Speicher sollte nur
fürs Backup dienen, nicht für die Live-Datenbank.

Ein Backup
ist das Kopieren von `cliphop.db` (im laufenden Betrieb mit
`sqlite3 cliphop.db ".backup …"` oder im Stillstand per Dateikopie). Es gibt
keinen weiteren Zustand.

## HAProxy und Traefik

Für `cliphop.rohwer.sh` ist in **HAProxy** nichts zu tun: nicht explizit
geroutete Hosts gehen an Traefik, das per Host-Regel (Label) an die App routet.

Auf dem Router für diese App dürfen **keine** `compress`- oder
`buffering`-Middlewares liegen. Der SSE-Stream (`text/event-stream`) muss
ungepuffert durchlaufen, sonst erreichen Änderungen die Clients verzögert oder
gar nicht.

Empfehlungen für die Kette:

- Keine Kompressions-Middleware; `text/event-stream` nicht komprimieren.
- Keine Puffer-Middleware in Traefik.
- Leerlauf-Timeouts (HAProxy `timeout client`/`timeout server`) größer als der
  Heartbeat halten. Der Server sendet alle ~20 s ein Lebenszeichen (`: ping`);
  `EventSource` im Browser verbindet sich bei einem Abbruch selbst neu und
  holt dabei den aktuellen Stand.
- Für korrekte Client-IPs in Logs läuft `uvicorn` mit
  `--proxy-headers --forwarded-allow-ips="*"` (siehe `Dockerfile`). Bei Bedarf
  auf das Traefik-Netz einschränken.

## Betrieb

- **Ein einziger Worker.** Die Live-Updates laufen über Pub/Sub im Prozess.
  Bei mehreren Workern bräuchte es einen externen Vermittler (z. B. Redis);
  der Compose-Service startet bewusst einen Worker.
- **Keine Authentifizierung.** Der Hostname ist nur im LAN auflösbar; jeder im
  LAN kann lesen und schreiben. OIDC über authentik ist ein geplanter,
  separater Change.
