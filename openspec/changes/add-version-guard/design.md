# Design

## Context

Siehe `proposal.md` — Why. Bestand, auf dem aufgesetzt wird:

- Die Version steht real an **sechs Dateien / sieben Stellen**: `pyproject.toml`,
  `Dockerfile` (`ARG VERSION`), `compose.yaml` (Image-Tag),
  `src/cliphop/__init__.py` (`__version__`), `docs/DEPLOYMENT.md` (zwei
  Beispielbefehle) und `uv.lock` (abgeleitet).
- `AGENTS.md` behauptet „drei Stellen" und nennt nur drei.
- Es gibt **kein CI, kein Makefile/justfile, keine Skripte**. Tests laufen über
  `uv run pytest` und liegen in `tests/` (z. B. `tests/test_api.py`).
- `pyproject.toml` speist die Paket-Metadaten; `uv lock` leitet daraus die
  Version in `uv.lock` ab.

## Goals / Non-Goals

**Goals:**

- Eine einzige Definition der Versionsstellen, damit Prüfung und Bump nicht
  auseinanderlaufen.
- Ein Befehl setzt die Version überall und aktualisiert `uv.lock`.
- Abweichungen fallen bei `uv run pytest` auf — ohne Netz, ohne Image-Build.

**Non-Goals:**

- Keine CI-Pipeline, keine Git-Hooks, kein automatisches Hochzählen (keine
  SemVer-Logik).
- Keine Single Source of Truth über Paket-Metadaten: `__version__` bleibt eine
  explizite Stelle.
- Kein Eingriff in Anwendungsverhalten oder Container.

## Decisions

**1. Bump-Skript `scripts/bump_version.py` mit `--check`.**
Ein Python-Skript (Repo ist Python/uv), das eine Liste von Stellen
(Datei + Regex mit genau einer Erfassungsgruppe) hält. `bump <version>` ersetzt
alle und führt danach `uv lock` aus; `--check` vergleicht alle gegen die Version
aus `pyproject.toml` und beendet sich mit Fehlercode, wenn etwas abweicht.
*Alternative:* Shell-Skript mit `sed` — schlechter lesbar und ohne saubere
Prüf-Logik. *Alternative:* nur ein Test — prüft, setzt aber nichts; man müsste
weiter von Hand editieren.

**2. Die Stellenliste lebt nur im Skript; der Test ruft `--check` auf.**
`tests/test_version.py` startet das Skript mit `sys.executable … --check` und
erwartet Rückgabecode 0. So gibt es keine zweite Kopie der Liste, und der Test
prüft zugleich das Werkzeug. *Alternative:* Liste im Test duplizieren — zwei
Wahrheiten, die auseinanderlaufen können.

**3. `pyproject.toml` ist die kanonische Quelle.**
`--check` liest die Soll-Version aus `pyproject.toml` und prüft alle anderen
Stellen dagegen. *Alternative:* eine separate Versionsdatei — zusätzliche Stelle.

**4. `uv.lock` wird mitgeprüft.**
`--check` liest die Version des Pakets `cliphop` aus `uv.lock` und vergleicht
sie; so fällt auf, wenn nach einem manuellen Bump `uv lock` vergessen wurde.
*Alternative:* auslassen — dann kann `uv.lock` still veralten.

**5. `docs/DEPLOYMENT.md` gehört zur Menge.**
Die beiden Beispielbefehle tragen die konkrete Version; sie werden mitgesetzt
und mitgeprüft, damit die dokumentierte Anleitung nicht veraltet.

**6. `AGENTS.md` wird richtiggestellt.**
Statt „drei Stellen" die tatsächlichen Stellen nennen, dazu den Bump-Befehl
(`uv run python scripts/bump_version.py <version>`) und den Prüflauf
(`uv run pytest`).

## Risks / Trade-offs

- **Regex-Ersetzen könnte zu breit greifen** → je Stelle ein enges, auf die Zeile
  zugeschnittenes Muster mit genau einer Erfassungsgruppe; das Skript bricht ab,
  wenn ein Muster nicht genau einmal trifft.
- **Test hängt an Pfad/Arbeitsverzeichnis** → Repo-Wurzel aus `__file__`
  ableiten, nicht aus dem CWD.
- **Kein CI** → der Test wirkt nur, wenn jemand `uv run pytest` ausführt;
  `AGENTS.md` hält fest, dass vor dem Bump/Commit zu prüfen ist.
- **Doku-Prüfung kann bei Umformulierungen stören** → akzeptiert; die
  Beispielbefehle sind stabil.

## Migration Plan

- Reine Werkzeug-Ergänzung; keine Daten- oder Container-Migration.
- Rollback: die neuen Dateien entfernen und `AGENTS.md` zurücksetzen.
