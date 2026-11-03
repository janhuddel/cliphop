"""Jinja2-Umgebung und Render-Hilfen für die Fragmente."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .db import Item

_TEMPLATES_DIR = Path(__file__).parent / "templates"

_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"]),
)


def render_list(items: list[Item], error: str | None = None) -> str:
    """Rendert den Listen-Ausschnitt (Slot, Verlauf, Meldung)."""
    return _env.get_template("_list.html").render(items=items, error=error)


def render_page(items: list[Item]) -> str:
    """Rendert die vollständige Seite."""
    return _env.get_template("index.html").render(items=items)
