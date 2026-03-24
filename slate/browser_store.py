from __future__ import annotations

import sqlite3
from pathlib import Path

from .browser import Bookmark, BrowserModule, BrowserTab, DownloadJob, HistoryEntry
from .db import initialize_database

DEFAULT_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "db" / "schema.sql"


class BrowserStore:
    """SQLite-backed persistence for Phase 2 browser state."""

    def __init__(self, db_path: Path, schema_path: Path = DEFAULT_SCHEMA_PATH) -> None:
        self.db_path = db_path
        self.schema_path = schema_path

    def initialize(self) -> None:
        initialize_database(self.db_path, self.schema_path)

    def save_snapshot(
        self,
        user_id: str,
        browser: BrowserModule,
        workspace_id: str | None = None,
        session_id: str | None = None,
    ) -> None:
        self.initialize()
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("DELETE FROM browser_tabs WHERE user_id = ?", (user_id,))
            connection.execute("DELETE FROM browser_bookmarks WHERE user_id = ?", (user_id,))
            connection.execute("DELETE FROM browser_history WHERE user_id = ?", (user_id,))
            connection.execute("DELETE FROM browser_downloads WHERE user_id = ?", (user_id,))
            connection.execute("DELETE FROM browser_adblock_rules WHERE user_id = ?", (user_id,))

            for position, tab in enumerate(browser.tabs):
                connection.execute(
                    """
                    INSERT INTO browser_tabs (
                      id, user_id, workspace_id, session_id, url, title, is_pinned, position, created_at, last_accessed
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, strftime('%s','now'), strftime('%s','now'))
                    """,
                    (
                        tab.id,
                        user_id,
                        workspace_id,
                        session_id,
                        tab.url,
                        tab.title,
                        1 if tab.is_pinned else 0,
                        position,
                    ),
                )

            for bookmark in browser.bookmarks:
                connection.execute(
                    """
                    INSERT INTO browser_bookmarks (user_id, url, title, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user_id, bookmark.url, bookmark.title, bookmark.created_at),
                )

            for entry in browser.history(limit=1000):
                connection.execute(
                    """
                    INSERT INTO browser_history (user_id, url, title, visited_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user_id, entry.url, entry.title, entry.visited_at),
                )

            for download in browser.downloads:
                connection.execute(
                    """
                    INSERT INTO browser_downloads (id, user_id, url, status, saved_path, created_at)
                    VALUES (?, ?, ?, ?, ?, strftime('%s','now'))
                    """,
                    (download.id, user_id, download.url, download.status, download.saved_path),
                )

            for pattern in sorted(browser._adblock_rules):
                connection.execute(
                    """
                    INSERT INTO browser_adblock_rules (user_id, pattern, created_at)
                    VALUES (?, ?, strftime('%s','now'))
                    """,
                    (user_id, pattern),
                )

            connection.commit()

    def load_snapshot(self, user_id: str) -> BrowserModule:
        self.initialize()
        browser = BrowserModule()

        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row

            tabs = connection.execute(
                """
                SELECT id, url, title, is_pinned
                FROM browser_tabs
                WHERE user_id = ?
                ORDER BY position ASC, created_at ASC
                """,
                (user_id,),
            ).fetchall()
            for index, row in enumerate(tabs):
                browser_tab = BrowserTab(
                    id=row["id"],
                    url=row["url"],
                    title=row["title"] or row["url"],
                    is_pinned=bool(row["is_pinned"]),
                    is_active=index == 0,
                )
                browser._tabs[browser_tab.id] = browser_tab

            bookmarks = connection.execute(
                """
                SELECT url, title, created_at
                FROM browser_bookmarks
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            ).fetchall()
            for row in bookmarks:
                bookmark = Bookmark(url=row["url"], title=row["title"], created_at=row["created_at"])
                browser._bookmarks[bookmark.url] = bookmark

            history = connection.execute(
                """
                SELECT url, title, visited_at
                FROM browser_history
                WHERE user_id = ?
                ORDER BY id DESC
                """,
                (user_id,),
            ).fetchall()
            browser._history = [
                HistoryEntry(url=row["url"], title=row["title"], visited_at=row["visited_at"]) for row in history
            ]

            downloads = connection.execute(
                """
                SELECT id, url, status, saved_path
                FROM browser_downloads
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            ).fetchall()
            browser._downloads = {
                row["id"]: DownloadJob(
                    id=row["id"],
                    url=row["url"],
                    status=row["status"],
                    saved_path=row["saved_path"],
                )
                for row in downloads
            }

            rules = connection.execute(
                """
                SELECT pattern
                FROM browser_adblock_rules
                WHERE user_id = ?
                ORDER BY id ASC
                """,
                (user_id,),
            ).fetchall()
            browser._adblock_rules = {row["pattern"].lower() for row in rules}

        return browser
