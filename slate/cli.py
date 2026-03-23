from __future__ import annotations

import argparse
from pathlib import Path

from .app import Slate
from .browser import SLATE_MAKER
from .roadmap import DELIVERY_PHASES
from .status import incomplete_phases, load_roadmap_status


DEFAULT_PATH = Path.home() / ".slate" / "surfaces.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Slate: one surface for everything")
    parser.add_argument("--store", type=Path, default=DEFAULT_PATH, help="Location for slate data")

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a surface")
    add_parser.add_argument("title")
    add_parser.add_argument("body")
    add_parser.add_argument("--tag", action="append", default=[])

    subparsers.add_parser("list", help="List all surfaces")

    search_parser = subparsers.add_parser("search", help="Search surfaces")
    search_parser.add_argument("query")

    subparsers.add_parser("roadmap", help="Show the 18-week delivery roadmap")
    subparsers.add_parser("status", help="Show current roadmap completion status")

    return parser


def format_surface(index: int, title: str, body: str, tags: list[str]) -> str:
    tags_part = ", ".join(tags) if tags else "no tags"
    return f"{index:>2}. {title}\n    {body}\n    [{tags_part}]"


def render_results(title: str, surfaces: list) -> int:
    print(title)
    print("-" * len(title))
    if not surfaces:
        print("No surfaces found.")
        return 0

    for index, surface in enumerate(surfaces, start=1):
        print(format_surface(index, surface.title, surface.body, surface.tags))
    print(f"\nTotal: {len(surfaces)}")
    return 0


def main() -> int:
    args = build_parser().parse_args()
    slate = Slate(args.store)

    if args.command == "add":
        surface = slate.add_surface(args.title, args.body, tags=args.tag)
        print(f"Added: {surface.title} (tags: {len(surface.tags)})")
        return 0

    if args.command == "list":
        return render_results("All surfaces", slate.surfaces)

    if args.command == "search":
        matches = slate.search(args.query)
        return render_results(f"Search results for '{args.query}'", matches)

    if args.command == "roadmap":
        print(f"Slate delivery roadmap — {SLATE_MAKER}")
        print("---------------------")
        for phase in DELIVERY_PHASES:
            print(f"{phase.id}. {phase.name} ({phase.weeks})")
            for deliverable in phase.deliverables:
                print(f"   - {deliverable}")
        return 0

    if args.command == "status":
        status = load_roadmap_status()
        remaining = incomplete_phases(len(DELIVERY_PHASES), status.completed_phases)

        print(f"Roadmap status — {SLATE_MAKER}")
        print("--------------")
        print(f"Active phase: {status.active_phase}")
        print(f"Completed phases: {list(status.completed_phases)}")
        print(f"Incomplete phases: {list(remaining)}")
        if status.notes:
            print(f"Notes: {status.notes}")
        print(
            f"Tell me to continue and I will start Phase {status.active_phase}, or tell me you are done for now."
        )
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
