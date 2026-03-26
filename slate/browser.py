from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

SLATE_MAKER = "VOIDENMARK"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class BrowserTab:
    id: str
    url: str
    title: str
    is_pinned: bool = False
    is_active: bool = False


@dataclass(slots=True)
class Bookmark:
    url: str
    title: str
    created_at: str = field(default_factory=_now_iso)


@dataclass(slots=True)
class HistoryEntry:
    url: str
    title: str
    visited_at: str = field(default_factory=_now_iso)


@dataclass(slots=True)
class DownloadJob:
    id: str
    url: str
    status: str = "queued"
    saved_path: str | None = None


class BrowserModule:
    def __init__(self) -> None:
        self._tabs: dict[str, BrowserTab] = {}
        self._history: list[HistoryEntry] = []
        self._bookmarks: dict[str, Bookmark] = {}
        self._downloads: dict[str, DownloadJob] = {}
        self._adblock_rules: set[str] = set()

    @property
    def tabs(self) -> tuple[BrowserTab, ...]:
        return tuple(sorted(self._tabs.values(), key=lambda tab: (not tab.is_pinned, tab.id)))

    def open_tab(self, tab_id: str, url: str, title: str | None = None) -> BrowserTab:
        if tab_id in self._tabs:
            raise ValueError(f'Tab with id "{tab_id}" already exists.')

        tab = BrowserTab(
            id=tab_id,
            url=url,
            title=title or url,
            is_active=not self._tabs,
        )
        self._tabs[tab_id] = tab
        self.record_visit(url, tab.title)
        return tab

    def close_tab(self, tab_id: str) -> bool:
        tab = self._tabs.get(tab_id)
        if tab is None:
            return False

        was_active = tab.is_active
        del self._tabs[tab_id]

        if was_active and self._tabs:
            first = next(iter(self.tabs))
            first.is_active = True

        return True

    def activate_tab(self, tab_id: str) -> BrowserTab:
        if tab_id not in self._tabs:
            raise ValueError(f"Unknown tab: {tab_id}")

        for tab in self._tabs.values():
            tab.is_active = False

        self._tabs[tab_id].is_active = True
        return self._tabs[tab_id]

    def navigate_tab(self, tab_id: str, url: str) -> BrowserTab:
        if tab_id not in self._tabs:
            raise ValueError(f"Unknown tab: {tab_id}")

        tab = self._tabs[tab_id]
        tab.url = url
        tab.title = url
        self.record_visit(url, url)
        return tab

    def pin_tab(self, tab_id: str, pinned: bool = True) -> BrowserTab:
        if tab_id not in self._tabs:
            raise ValueError(f"Unknown tab: {tab_id}")

        self._tabs[tab_id].is_pinned = pinned
        return self._tabs[tab_id]

    def add_bookmark(self, url: str, title: str | None = None) -> Bookmark:
        bookmark = Bookmark(url=url, title=title or url)
        self._bookmarks[url] = bookmark
        return bookmark

    def remove_bookmark(self, url: str) -> bool:
        return self._bookmarks.pop(url, None) is not None

    @property
    def bookmarks(self) -> tuple[Bookmark, ...]:
        return tuple(sorted(self._bookmarks.values(), key=lambda item: item.title.lower()))

    def record_visit(self, url: str, title: str | None = None) -> HistoryEntry:
        entry = HistoryEntry(url=url, title=title or url)
        self._history.insert(0, entry)
        return entry

    def history(self, limit: int = 20) -> tuple[HistoryEntry, ...]:
        return tuple(self._history[: max(0, limit)])

    def add_adblock_rule(self, pattern: str) -> int:
        self._adblock_rules.add(pattern.lower())
        return len(self._adblock_rules)

    def remove_adblock_rule(self, pattern: str) -> bool:
        normalized = pattern.lower()
        if normalized not in self._adblock_rules:
            return False
        self._adblock_rules.remove(normalized)
        return True

    @property
    def adblock_rules(self) -> tuple[str, ...]:
        return tuple(sorted(self._adblock_rules))

    def is_blocked(self, url: str) -> bool:
        lower_url = url.lower()
        return any(pattern in lower_url for pattern in self._adblock_rules)

    def queue_download(self, download_id: str, url: str) -> DownloadJob:
        if download_id in self._downloads:
            raise ValueError(f'Download with id "{download_id}" already exists.')

        job = DownloadJob(id=download_id, url=url)
        self._downloads[download_id] = job
        return job

    def update_download(self, download_id: str, status: str, saved_path: str | None = None) -> DownloadJob:
        if download_id not in self._downloads:
            raise ValueError(f"Unknown download: {download_id}")

        job = self._downloads[download_id]
        job.status = status
        job.saved_path = saved_path
        return job

    @property
    def downloads(self) -> tuple[DownloadJob, ...]:
        return tuple(self._downloads.values())

    def webview_ipc(self, tab_id: str) -> dict[str, object]:
        if tab_id not in self._tabs:
            raise ValueError(f"Unknown tab: {tab_id}")

        from .ipc import create_webview_ipc

        tab = self._tabs[tab_id]
        return create_webview_ipc(
            tab_id=tab.id, url=tab.url, ad_blocked=self.is_blocked(tab.url)
        ).to_dict()

    def to_dict(self) -> dict[str, object]:
        return {
            "maker": SLATE_MAKER,
            "tabs": [asdict(tab) for tab in self.tabs],
            "bookmarks": [asdict(bookmark) for bookmark in self.bookmarks],
            "history": [asdict(entry) for entry in self.history()],
            "downloads": [asdict(download) for download in self.downloads],
            "ad_block_rules": list(self.adblock_rules),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "BrowserModule":
        browser = cls()

        for item in payload.get("tabs", []):
            tab = BrowserTab(**item)
            browser._tabs[tab.id] = tab

        for item in payload.get("bookmarks", []):
            bookmark = Bookmark(**item)
            browser._bookmarks[bookmark.url] = bookmark

        browser._history = [HistoryEntry(**item) for item in payload.get("history", [])]
        browser._downloads = {
            job.id: job for job in (DownloadJob(**item) for item in payload.get("downloads", []))
        }
        browser._adblock_rules = {str(rule).lower() for rule in payload.get("ad_block_rules", [])}
        return browser
