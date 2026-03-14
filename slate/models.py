from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class Surface:
    """A single piece of information managed by Slate."""

    title: str
    body: str
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=utc_now)

    def matches(self, query: str) -> bool:
        target = " ".join([self.title, self.body, *self.tags]).lower()
        return query.lower() in target
