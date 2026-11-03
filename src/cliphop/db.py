"""SQLite-Speicher für Einträge inklusive TTL-Aufräumen und Obergrenze."""

from __future__ import annotations

import sqlite3
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

_SCHEMA = """
CREATE TABLE IF NOT EXISTS item (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    content    TEXT    NOT NULL,
    created_at REAL    NOT NULL,
    pinned     INTEGER NOT NULL DEFAULT 0
);
"""


@dataclass(frozen=True)
class Item:
    """Ein einzelner Eintrag."""

    id: int
    content: str
    created_at: float
    pinned: bool


class Store:
    """Zugriffsschicht auf die SQLite-Datei."""

    def __init__(
        self,
        db_path: str,
        ttl_seconds: int,
        max_items: int,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self.ttl_seconds = ttl_seconds
        self.max_items = max_items
        self._clock = clock
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    # -- Hilfen ---------------------------------------------------------

    def _now(self, now: float | None) -> float:
        return self._clock() if now is None else now

    @staticmethod
    def _to_item(row: sqlite3.Row) -> Item:
        return Item(
            id=row["id"],
            content=row["content"],
            created_at=row["created_at"],
            pinned=bool(row["pinned"]),
        )

    def _fetch(self, item_id: int) -> Item | None:
        row = self._conn.execute(
            "SELECT id, content, created_at, pinned FROM item WHERE id = ?",
            (item_id,),
        ).fetchone()
        return None if row is None else self._to_item(row)

    # -- Aufräumen ------------------------------------------------------

    def prune(self, now: float | None = None) -> int:
        """Entfernt abgelaufene ungepinnte Einträge und solche über der Obergrenze."""
        ts = self._now(now)
        cutoff = ts - self.ttl_seconds
        removed = self._conn.execute(
            "DELETE FROM item WHERE pinned = 0 AND created_at < ?",
            (cutoff,),
        ).rowcount
        removed += self._conn.execute(
            "DELETE FROM item WHERE pinned = 0 AND id NOT IN ("
            "  SELECT id FROM item WHERE pinned = 0"
            "  ORDER BY created_at DESC, id DESC LIMIT ?"
            ")",
            (self.max_items,),
        ).rowcount
        self._conn.commit()
        return removed

    # -- Lesen und Schreiben -------------------------------------------

    def list_items(self, now: float | None = None) -> list[Item]:
        """Liefert alle Einträge, neueste zuerst; räumt zuvor auf."""
        self.prune(now)
        rows = self._conn.execute(
            "SELECT id, content, created_at, pinned FROM item"
            " ORDER BY created_at DESC, id DESC"
        ).fetchall()
        return [self._to_item(row) for row in rows]

    def add(self, content: str, now: float | None = None) -> Item:
        """Legt einen Eintrag an; leerer oder reiner Leerraum wird abgelehnt."""
        if content is None or not content.strip():
            raise ValueError("Eintrag darf nicht leer sein")
        ts = self._now(now)
        cursor = self._conn.execute(
            "INSERT INTO item (content, created_at, pinned) VALUES (?, ?, 0)",
            (content, ts),
        )
        self._conn.commit()
        self.prune(ts)
        return Item(id=int(cursor.lastrowid), content=content, created_at=ts, pinned=False)

    def delete(self, item_id: int, now: float | None = None) -> bool:
        """Löscht einen Eintrag, unabhängig von seinem Pin-Zustand."""
        cursor = self._conn.execute("DELETE FROM item WHERE id = ?", (item_id,))
        self._conn.commit()
        self.prune(now)
        return cursor.rowcount > 0

    def toggle_pin(self, item_id: int, now: float | None = None) -> Item | None:
        """Schaltet den Pin eines Eintrags um; ``None``, wenn er nicht existiert."""
        item = self._fetch(item_id)
        if item is None:
            return None
        self._conn.execute(
            "UPDATE item SET pinned = ? WHERE id = ?",
            (0 if item.pinned else 1, item_id),
        )
        self._conn.commit()
        self.prune(now)
        return self._fetch(item_id)

    def clear(self, include_pinned: bool = False, now: float | None = None) -> int:
        """Leert die Liste; gepinnte Einträge nur bei ``include_pinned``."""
        if include_pinned:
            cursor = self._conn.execute("DELETE FROM item")
        else:
            cursor = self._conn.execute("DELETE FROM item WHERE pinned = 0")
        self._conn.commit()
        return cursor.rowcount
