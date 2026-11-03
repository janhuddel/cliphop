# Tasks

## 1. Bump-Skript

- [x] 1.1 In `scripts/bump_version.py` die Stellenliste (Datei + Regex mit genau einer Erfassungsgruppe) für `pyproject.toml`, `Dockerfile`, `compose.yaml`, `src/cliphop/__init__.py`, `docs/DEPLOYMENT.md` und `uv.lock` anlegen sowie die beiden Modi `bump <version>` (ersetzt alle Stellen und ruft `uv lock`) und `--check` (vergleicht alles gegen die Version aus `pyproject.toml`, ohne zu schreiben) implementieren; verifizieren, dass `uv run python scripts/bump_version.py --check` mit Rückgabecode 0 endet
- [x] 1.2 Absichern, dass `--check` eine Abweichung erkennt: eine Stelle temporär verstellen, `--check` laufen lassen und verifizieren, dass es mit Rückgabecode ≠ 0 abbricht und die abweichende Stelle nennt; danach die Verstellung zurücknehmen und erneut 0 verifizieren
- [x] 1.3 Absichern, dass `bump` idempotent und vollständig ist: auf eine Testversion bumpen, verifizieren, dass alle Stellen inklusive `uv.lock` übereinstimmen, und anschließend auf `1.0.3` zurückbumpen und `--check` erneut grün sehen

## 2. Test

- [x] 2.1 `tests/test_version.py` ergänzen, das `scripts/bump_version.py --check` über `sys.executable` mit aus `__file__` abgeleiteter Repo-Wurzel aufruft; verifizieren, dass `uv run pytest` grün ist und bei einer künstlich verstellten Stelle rot wird

## 3. Dokumentation

- [x] 3.1 `AGENTS.md` richtigstellen: die tatsächlichen Versionsstellen auflisten, den Bump-Befehl `uv run python scripts/bump_version.py <version>` und den Prüflauf `uv run pytest` nennen und die Aussage „steht an drei Stellen" entfernen; verifizieren, dass `AGENTS.md` keine „drei Stellen"-Aussage mehr enthält und die genannten Dateien zur Stellenliste des Skripts passen
- [x] 3.2 `docs/DEPLOYMENT.md` richtigstellen: die Prosa „beim Versionssprung alle drei Stellen anpassen" durch die tatsächlichen Stellen und den Bump-/Prüfbefehl ersetzen (die Beispielbefehle tragen die Version bereits); verifizieren, dass `docs/DEPLOYMENT.md` keine „drei Stellen"-Aussage mehr enthält und zur Stellenliste des Skripts passt

## Workflow follow-up

- Change nach abgeschlossenem Review archivieren.
- Ergebnis nach dem Archivieren prüfen.
