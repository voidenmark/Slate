from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class DeliveryPhase:
    id: int
    name: str
    weeks: str
    deliverables: tuple[str, ...]


@dataclass(slots=True)
class DeliveryPhaseStatus:
    phase: DeliveryPhase
    status: str = "pending"
    completed_deliverables: list[str] = field(default_factory=list)

    def complete_deliverable(self, deliverable: str) -> None:
        if deliverable not in self.phase.deliverables:
            raise ValueError(f"Unknown deliverable: {deliverable}")

        if deliverable in self.completed_deliverables:
            return

        self.completed_deliverables.append(deliverable)
        self.status = "completed" if len(self.completed_deliverables) == len(self.phase.deliverables) else "in_progress"


DELIVERY_PHASES: tuple[DeliveryPhase, ...] = (
    DeliveryPhase(
        id=1,
        name="Foundation",
        weeks="Weeks 1-2",
        deliverables=(
            "Project setup and folder structure",
            "Database initialization",
            "Core architecture (IPC, state management)",
            "Basic layout with three columns",
            "Universal search shell",
        ),
    ),
    DeliveryPhase(
        id=2,
        name="Browser Module",
        weeks="Weeks 3-4",
        deliverables=(
            "Tab management",
            "WebView integration",
            "Bookmarks & history",
            "Ad blocking",
            "Downloads",
        ),
    ),
    DeliveryPhase(
        id=3,
        name="Notes Module",
        weeks="Weeks 5-6",
        deliverables=(
            "TipTap/BlockNote editor",
            "Rich text blocks",
            "Folder organization",
            "Database tables (Notion-like)",
        ),
    ),
    DeliveryPhase(
        id=4,
        name="Communication",
        weeks="Weeks 7-8",
        deliverables=(
            "Email (IMAP/SMTP)",
            "AI categorization",
            "Multi-protocol chat (WhatsApp, Discord)",
            "Unified messaging",
        ),
    ),
    DeliveryPhase(
        id=5,
        name="Media",
        weeks="Weeks 9-10",
        deliverables=(
            "YouTube integration",
            "Video player with PiP",
            "Spotify/music player",
            "Podcast RSS feeds",
        ),
    ),
    DeliveryPhase(
        id=6,
        name="Code & Work",
        weeks="Weeks 11-14",
        deliverables=(
            "Monaco editor",
            "Terminal integration",
            "Git operations",
            "Kanban boards",
            "Calendar sync",
        ),
    ),
    DeliveryPhase(
        id=7,
        name="Advanced Features",
        weeks="Weeks 15-16",
        deliverables=(
            "Finance (Plaid)",
            "Design tools",
            "AI Assistant (Claude)",
            "Extension system",
        ),
    ),
    DeliveryPhase(
        id=8,
        name="Polish & Optimization",
        weeks="Weeks 17-18",
        deliverables=(
            "Performance tuning",
            "Memory leak fixes",
            "UI polish",
            "Accessibility",
        ),
    ),
)


def build_execution_plan() -> list[DeliveryPhaseStatus]:
    return [DeliveryPhaseStatus(phase=phase) for phase in DELIVERY_PHASES]


def execution_progress(plan: list[DeliveryPhaseStatus]) -> float:
    total_deliverables = sum(len(item.phase.deliverables) for item in plan)
    completed_deliverables = sum(len(item.completed_deliverables) for item in plan)

    if total_deliverables == 0:
        return 0.0

    return completed_deliverables / total_deliverables
