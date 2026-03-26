from __future__ import annotations

import argparse
from pathlib import Path

from .app import Slate
from .browser import SLATE_MAKER
from .browser_store import BrowserStore
from .roadmap import DELIVERY_PHASES
from .status import incomplete_phases, load_roadmap_status


DEFAULT_PATH = Path.home() / ".slate" / "surfaces.json"
DEFAULT_DB_PATH = Path.home() / ".slate" / "slate.db"


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

    notes_parser = subparsers.add_parser("notes", help="Notes module operations")
    notes_subcommands = notes_parser.add_subparsers(dest="notes_command", required=True)

    notes_create = notes_subcommands.add_parser("create", help="Create a new note")
    notes_create.add_argument("user_id")
    notes_create.add_argument("note_id")
    notes_create.add_argument("title")

    notes_add_block = notes_subcommands.add_parser("add-block", help="Add a block to a note")
    notes_add_block.add_argument("user_id")
    notes_add_block.add_argument("note_id")
    notes_add_block.add_argument("block_id")
    notes_add_block.add_argument("type", choices=["text", "heading", "image", "code"])
    notes_add_block.add_argument("content")

    notes_list = notes_subcommands.add_parser("list", help="List notes for a user")
    notes_list.add_argument("user_id")

    browser_parser = subparsers.add_parser("browser", help="Persisted browser operations")
    browser_subcommands = browser_parser.add_subparsers(dest="browser_command", required=True)

    browser_open = browser_subcommands.add_parser("open", help="Open a browser tab for a user")
    browser_open.add_argument("user_id")
    browser_open.add_argument("tab_id")
    browser_open.add_argument("url")
    browser_open.add_argument("--title", default=None)
    browser_open.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)

    browser_close = browser_subcommands.add_parser("close", help="Close a browser tab")
    browser_close.add_argument("user_id")
    browser_close.add_argument("tab_id")
    browser_close.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)

    browser_activate = browser_subcommands.add_parser("activate", help="Activate a browser tab")
    browser_activate.add_argument("user_id")
    browser_activate.add_argument("tab_id")
    browser_activate.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)

    browser_navigate = browser_subcommands.add_parser("navigate", help="Navigate an existing tab to a URL")
    browser_navigate.add_argument("user_id")
    browser_navigate.add_argument("tab_id")
    browser_navigate.add_argument("url")
    browser_navigate.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)

    browser_pin = browser_subcommands.add_parser("pin", help="Pin or unpin a browser tab")
    browser_pin.add_argument("user_id")
    browser_pin.add_argument("tab_id")
    browser_pin.add_argument("--off", action="store_true", help="Unpin tab instead of pinning")
    browser_pin.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)

    browser_bookmark = browser_subcommands.add_parser("bookmark", help="Bookmark a URL for a user")
    browser_bookmark.add_argument("user_id")
    browser_bookmark.add_argument("url")
    browser_bookmark.add_argument("--title", default=None)
    browser_bookmark.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)

    browser_unbookmark = browser_subcommands.add_parser("unbookmark", help="Remove bookmark for a URL")
    browser_unbookmark.add_argument("user_id")
    browser_unbookmark.add_argument("url")
    browser_unbookmark.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)

    browser_addrule = browser_subcommands.add_parser("add-rule", help="Add an ad-block rule")
    browser_addrule.add_argument("user_id")
    browser_addrule.add_argument("pattern")
    browser_addrule.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)

    browser_removerule = browser_subcommands.add_parser("remove-rule", help="Remove an ad-block rule")
    browser_removerule.add_argument("user_id")
    browser_removerule.add_argument("pattern")
    browser_removerule.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)

    browser_download = browser_subcommands.add_parser("download", help="Queue a browser download")
    browser_download.add_argument("user_id")
    browser_download.add_argument("download_id")
    browser_download.add_argument("url")
    browser_download.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)

    browser_webview = browser_subcommands.add_parser("webview", help="Show webview config for a tab")
    browser_webview.add_argument("user_id")
    browser_webview.add_argument("tab_id")
    browser_webview.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)

    browser_ipc_webview = browser_subcommands.add_parser("ipc-webview", help="Show formal webview IPC message")
    browser_ipc_webview.add_argument("user_id")
    browser_ipc_webview.add_argument("tab_id")
    browser_ipc_webview.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)

    browser_download_status = browser_subcommands.add_parser("download-status", help="Update download status")
    browser_download_status.add_argument("user_id")
    browser_download_status.add_argument("download_id")
    browser_download_status.add_argument("status", choices=["queued", "in_progress", "completed", "failed"])
    browser_download_status.add_argument("--saved-path", default=None)
    browser_download_status.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)

    browser_subcommands.add_parser("list-tabs", help="List persisted browser tabs for a user")
    browser_subcommands.add_parser("list-bookmarks", help="List persisted bookmarks for a user")
    browser_subcommands.add_parser("list-downloads", help="List persisted downloads for a user")
    browser_subcommands.add_parser("list-rules", help="List persisted ad-block rules for a user")
    for subcommand in ("list-tabs", "list-bookmarks", "list-downloads", "list-rules"):
        parser_ref = browser_subcommands.choices[subcommand]
        parser_ref.add_argument("user_id")
        parser_ref.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)

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


def _handle_browser_command(args: argparse.Namespace) -> int:
    store = BrowserStore(args.db)
    browser = store.load_snapshot(args.user_id)

    if args.browser_command == "open":
        browser.open_tab(args.tab_id, args.url, args.title)
        store.save_snapshot(args.user_id, browser)
        print(f"Opened tab {args.tab_id} for {args.user_id}. Total tabs: {len(browser.tabs)}")
        return 0

    if args.browser_command == "close":
        closed = browser.close_tab(args.tab_id)
        store.save_snapshot(args.user_id, browser)
        print(f"Closed tab {args.tab_id}: {closed}. Total tabs: {len(browser.tabs)}")
        return 0

    if args.browser_command == "activate":
        browser.activate_tab(args.tab_id)
        store.save_snapshot(args.user_id, browser)
        print(f"Activated tab {args.tab_id} for {args.user_id}.")
        return 0

    if args.browser_command == "navigate":
        browser.navigate_tab(args.tab_id, args.url)
        store.save_snapshot(args.user_id, browser)
        print(f"Navigated tab {args.tab_id} to {args.url}.")
        return 0

    if args.browser_command == "pin":
        pinned = not args.off
        browser.pin_tab(args.tab_id, pinned)
        store.save_snapshot(args.user_id, browser)
        state = "pinned" if pinned else "unpinned"
        print(f"{state.capitalize()} tab {args.tab_id} for {args.user_id}.")
        return 0

    if args.browser_command == "bookmark":
        browser.add_bookmark(args.url, args.title)
        store.save_snapshot(args.user_id, browser)
        print(f"Saved bookmark for {args.user_id}. Total bookmarks: {len(browser.bookmarks)}")
        return 0

    if args.browser_command == "unbookmark":
        removed = browser.remove_bookmark(args.url)
        store.save_snapshot(args.user_id, browser)
        print(f"Removed bookmark {args.url}: {removed}. Total bookmarks: {len(browser.bookmarks)}")
        return 0

    if args.browser_command == "add-rule":
        browser.add_adblock_rule(args.pattern)
        store.save_snapshot(args.user_id, browser)
        print(f"Added ad-block rule '{args.pattern}' for {args.user_id}.")
        return 0

    if args.browser_command == "remove-rule":
        removed = browser.remove_adblock_rule(args.pattern)
        store.save_snapshot(args.user_id, browser)
        print(f"Removed ad-block rule '{args.pattern}' for {args.user_id}: {removed}.")
        return 0

    if args.browser_command == "download":
        browser.queue_download(args.download_id, args.url)
        store.save_snapshot(args.user_id, browser)
        print(f"Queued download {args.download_id} for {args.user_id}.")
        return 0

    if args.browser_command == "webview":
        config = browser.webview_ipc(args.tab_id)
        print(f"WebView config for {args.tab_id}: {config}")
        return 0

    if args.browser_command == "ipc-webview":
        import json

        message = browser.webview_ipc(args.tab_id)
        print(json.dumps(message, indent=2))
        return 0

    if args.browser_command == "download-status":
        browser.update_download(args.download_id, args.status, args.saved_path)
        store.save_snapshot(args.user_id, browser)
        print(f"Updated download {args.download_id} to {args.status}.")
        return 0

    if args.browser_command == "list-tabs":
        print(f"Browser tabs — {args.user_id}")
        print("---------------------")
        for tab in browser.tabs:
            marker = "*" if tab.is_active else " "
            pin = " [pinned]" if tab.is_pinned else ""
            print(f"{marker} {tab.id}: {tab.title} <{tab.url}>{pin}")
        print(f"Total tabs: {len(browser.tabs)}")
        return 0

    if args.browser_command == "list-bookmarks":
        print(f"Browser bookmarks — {args.user_id}")
        print("---------------------------")
        for bookmark in browser.bookmarks:
            print(f"- {bookmark.title} <{bookmark.url}>")
        print(f"Total bookmarks: {len(browser.bookmarks)}")
        return 0

    if args.browser_command == "list-rules":
        print(f"Ad-block rules — {args.user_id}")
        print("-------------------------")
        for pattern in browser.adblock_rules:
            print(f"- {pattern}")
        print(f"Total rules: {len(browser.adblock_rules)}")
        return 0

    if args.browser_command == "list-downloads":
        print(f"Browser downloads — {args.user_id}")
        print("--------------------------")
        for download in browser.downloads:
            saved = f" -> {download.saved_path}" if download.saved_path else ""
            print(f"- {download.id}: {download.status} <{download.url}>{saved}")
        print(f"Total downloads: {len(browser.downloads)}")
        return 0

    return 1


def _handle_notes_command(args: argparse.Namespace) -> int:
    from .notes import NotesModule

    # Notes module is in-memory for now in this foundational step
    # Real persistence will follow in subsequent steps of Phase 3
    notes_module = NotesModule(args.user_id)

    if args.notes_command == "create":
        note = notes_module.create_note(args.note_id, args.title)
        print(f"Created note '{note.title}' (ID: {note.id}) for {args.user_id}.")
        return 0

    if args.notes_command == "add-block":
        # In this mock-up foundation, we can't persist across CLI calls easily without a store
        # but for the sake of CLI structure:
        print(f"Added {args.type} block to note {args.note_id}.")
        return 0

    if args.notes_command == "list":
        print(f"Notes for {args.user_id}:")
        print("---------------------")
        # Empty for now since it's in-memory and we just started the module
        return 0

    return 1


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

    if args.command == "browser":
        return _handle_browser_command(args)

    if args.command == "notes":
        return _handle_notes_command(args)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
