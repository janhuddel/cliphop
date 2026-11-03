# Proposal

## Why

Die Versionsnummer steht in diesem Projekt an mehreren Stellen, wird aber nirgends
zusammengehalten: Es gibt keine Prüfung und keinen Befehl, der sie gemeinsam setzt.
Beim Sprung auf 1.0.3 sind genau deshalb `src/cliphop/__init__.py` und
`docs/DEPLOYMENT.md` zunächst übersehen worden, und `AGENTS.md` nennt fälschlich nur
drei Stellen. Ohne Absicherung wiederholt sich das beim nächsten Bump.

## What Changes

- **Neu:** ein Bump-Skript `scripts/bump_version.py`, das die Version an allen
  Stellen atomar setzt und danach `uv lock` ausführt. Ein `--check`-Modus meldet
  Abweichungen, ohne etwas zu schreiben.
- **Neu:** ein Test, der `--check` ausführt, sodass jede Abweichung bei
  `uv run pytest` auffällt.
- **Geändert:** `AGENTS.md` nennt die tatsächlichen Stellen und den Bump-Befehl
  statt „drei Stellen".

## Capabilities

### New Capabilities

<!-- Keine: reine Werkzeug-/Prozessänderung. Das Anwendungsverhalten von cliphop
     ändert sich nicht, deshalb keine neue Fähigkeit (skip_specs: true). -->

### Modified Capabilities

<!-- Keine: Es ändert sich keine Anforderung an das Systemverhalten. -->

## Impact

- **Neu:** `scripts/bump_version.py`, `tests/test_version.py`.
- **Geändert:** `AGENTS.md` (Dokumentation der Versionsstellen und des Befehls).
- **Unverändert:** Anwendungsverhalten, Endpunkte, Datenmodell, Abhängigkeiten,
  Container, Proxy-Kette.
