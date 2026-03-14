from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
import json
from pathlib import Path

from .models import Surface


class Slate:
    """A tiny file-backed organizer: one surface for everything."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._surfaces: list[Surface] = []
        self.load()

    @property
    def surfaces(self) -> list[Surface]:
        return list(self._surfaces)

    def add_surface(self, title: str, body: str, tags: list[str] | None = None) -> Surface:
        surface = Surface(title=title, body=body, tags=tags or [])
        self._surfaces.append(surface)
        self.save()
        return surface

    def search(self, query: str) -> list[Surface]:
        return [surface for surface in self._surfaces if surface.matches(query)]

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [{**asdict(surface), "created_at": surface.created_at.isoformat()} for surface in self._surfaces]
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def load(self) -> None:
        if not self.path.exists():
            self._surfaces = []
            return

        raw = json.loads(self.path.read_text(encoding="utf-8"))
        self._surfaces = [
            Surface(
                title=item["title"],
                body=item["body"],
                tags=item.get("tags", []),
                created_at=datetime.fromisoformat(item["created_at"]),
            )
            for item in raw
        ]
