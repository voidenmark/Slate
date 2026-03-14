from __future__ import annotations

import argparse
from pathlib import Path

from .app import Slate


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

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
