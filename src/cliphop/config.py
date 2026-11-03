"""Konfiguration aus Umgebungsvariablen."""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from dataclasses import dataclass

_DURATION_RE = re.compile(r"^\s*(\d+)\s*([smhd]?)\s*$", re.IGNORECASE)
_UNIT_SECONDS = {"": 1, "s": 1, "m": 60, "h": 3600, "d": 86400}


def parse_duration(text: str) -> int:
    """Wandelt eine Dauer wie ``24h``, ``30m`` oder ``45`` in Sekunden um."""
    match = _DURATION_RE.match(text)
    if match is None:
        raise ValueError(f"Ungültige Dauer: {text!r} (erwartet z. B. 30m, 24h, 7d)")
    value, unit = int(match.group(1)), match.group(2).lower()
    return value * _UNIT_SECONDS[unit]


@dataclass(frozen=True)
class Config:
    """Laufzeitkonfiguration der Anwendung."""

    db_path: str = "/data/cliphop.db"
    ttl_seconds: int = 24 * 3600
    max_items: int = 50
    base_url: str = "https://cliphop.rohwer.sh"
    sse_heartbeat_seconds: float = 20.0
    prune_interval_seconds: float = 60.0

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "Config":
        source = os.environ if env is None else env
        return cls(
            db_path=source.get("CLIPHOP_DB", cls.db_path),
            ttl_seconds=parse_duration(source.get("CLIPHOP_TTL", "24h")),
            max_items=int(source.get("CLIPHOP_MAX_ITEMS", str(cls.max_items))),
            base_url=source.get("BASE_URL", cls.base_url),
            sse_heartbeat_seconds=float(
                source.get("CLIPHOP_SSE_HEARTBEAT", str(cls.sse_heartbeat_seconds))
            ),
            prune_interval_seconds=float(
                source.get("CLIPHOP_PRUNE_INTERVAL", str(cls.prune_interval_seconds))
            ),
        )
