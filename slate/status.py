from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class RoadmapStatus:
    active_phase: int
    completed_phases: tuple[int, ...]
    notes: str


DEFAULT_STATUS_PATH = Path(__file__).resolve().parents[1] / "state" / "roadmap_status.json"


def load_roadmap_status(path: Path = DEFAULT_STATUS_PATH) -> RoadmapStatus:
    payload = json.loads(path.read_text(encoding="utf-8"))
    completed = tuple(sorted(set(payload.get("completed_phases", []))))

    return RoadmapStatus(
        active_phase=int(payload["active_phase"]),
        completed_phases=completed,
        notes=str(payload.get("notes", "")),
    )


def incomplete_phases(total_phases: int, completed_phases: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(phase for phase in range(1, total_phases + 1) if phase not in completed_phases)
