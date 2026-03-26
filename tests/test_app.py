import sys
from pathlib import Path

from slate.app import Slate
from slate.browser import BrowserModule, SLATE_MAKER
from slate.browser_store import BrowserStore
from slate.cli import format_surface, main, render_results
from slate.roadmap import DELIVERY_PHASES, build_execution_plan, execution_progress
from slate.status import incomplete_phases, load_roadmap_status


def test_add_and_persist_surface(tmp_path: Path) -> None:
    store = tmp_path / "surfaces.json"
    slate = Slate(store)

    created = slate.add_surface("Ideas", "Build Slate", tags=["todo", "product"])

    assert created.title == "Ideas"
    assert store.exists()

    reloaded = Slate(store)
    assert len(reloaded.surfaces) == 1
    assert reloaded.surfaces[0].tags == ["todo", "product"]


def test_search_by_content_and_tags(tmp_path: Path) -> None:
    slate = Slate(tmp_path / "surfaces.json")
    slate.add_surface("Roadmap", "Polish onboarding", tags=["product"])
    slate.add_surface("Bugfix", "Repair login form", tags=["engineering"])

    product_matches = slate.search("product")
    login_matches = slate.search("login")

    assert len(product_matches) == 1
    assert product_matches[0].title == "Roadmap"
    assert len(login_matches) == 1
    assert login_matches[0].title == "Bugfix"


def test_format_surface_has_readable_alignment() -> None:
    output = format_surface(2, "Ideas", "Build Slate", ["todo", "product"])

    assert output == " 2. Ideas\n    Build Slate\n    [todo, product]"


def test_render_results_handles_empty_state(capsys) -> None:
    exit_code = render_results("Search", [])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "No surfaces found." in captured.out


def test_initialize_database_creates_tables(tmp_path: Path) -> None:
    from slate.db import initialize_database

    db_path = tmp_path / "slate.db"
    schema_path = Path(__file__).resolve().parents[1] / "db" / "schema.sql"

    initialize_database(db_path, schema_path)

    import sqlite3

    with sqlite3.connect(db_path) as connection:
        table_names = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        }

    assert {"users", "workspaces", "browser_tabs", "browser_bookmarks", "browser_history", "browser_downloads", "browser_adblock_rules", "notes", "chat_conversations", "emails"}.issubset(table_names)


def test_build_execution_plan_has_eight_pending_phases() -> None:
    assert len(DELIVERY_PHASES) == 8

    plan = build_execution_plan()
    assert len(plan) == 8
    assert all(item.status == "pending" for item in plan)
    assert all(item.completed_deliverables == [] for item in plan)


def test_execution_progress_updates_when_deliverables_complete() -> None:
    plan = build_execution_plan()
    assert execution_progress(plan) == 0.0

    foundation = plan[0]
    foundation.complete_deliverable('Database initialization')

    assert foundation.status == 'in_progress'
    assert execution_progress(plan) > 0.0

    foundation.complete_deliverable('Project setup and folder structure')
    foundation.complete_deliverable('Core architecture (IPC, state management)')
    foundation.complete_deliverable('Basic layout with three columns')
    foundation.complete_deliverable('Universal search shell')

    assert foundation.status == 'completed'


def test_complete_deliverable_rejects_unknown_item() -> None:
    plan = build_execution_plan()

    try:
        plan[0].complete_deliverable('not-real')
    except ValueError as exc:
        assert 'Unknown deliverable' in str(exc)
    else:
        raise AssertionError('Expected ValueError for unknown deliverable')


def test_load_roadmap_status_and_incomplete_phases() -> None:
    status = load_roadmap_status()

    assert status.active_phase == 3
    assert status.completed_phases == (1, 2)
    assert incomplete_phases(len(DELIVERY_PHASES), status.completed_phases) == (3, 4, 5, 6, 7, 8)


def test_browser_module_phase_two_foundations() -> None:
    browser = BrowserModule()

    first = browser.open_tab('tab-1', 'https://example.com', 'Example')
    second = browser.open_tab('tab-2', 'https://news.example.com', 'News')

    assert first.is_active is True
    assert second.is_active is False

    browser.activate_tab('tab-2')
    assert browser.tabs[1].is_active is True

    browser.pin_tab('tab-2')
    assert browser.tabs[0].id == 'tab-2'

    browser.add_bookmark('https://example.com/docs', 'Docs')
    assert len(browser.bookmarks) == 1

    browser.add_adblock_rule('ads.')
    assert browser.is_blocked('https://ads.example.com/script.js') is True

    browser.queue_download('download-1', 'https://example.com/file.zip')
    browser.update_download('download-1', 'completed', '/tmp/file.zip')
    assert browser.downloads[0].status == 'completed'

    config = browser.webview_ipc('tab-2')
    assert config['payload']['url'] == 'https://news.example.com'

    assert browser.close_tab('tab-2') is True
    assert len(browser.history()) >= 2



def test_browser_module_round_trip_snapshot() -> None:
    browser = BrowserModule()
    browser.open_tab('tab-1', 'https://example.com')
    browser.navigate_tab('tab-1', 'https://docs.example.com')
    browser.add_bookmark('https://docs.example.com', 'Docs')
    browser.add_adblock_rule('ads.')
    browser.queue_download('download-2', 'https://example.com/archive.zip')

    snapshot = browser.to_dict()
    assert snapshot['maker'] == SLATE_MAKER

    restored = BrowserModule.from_dict(snapshot)
    assert restored.tabs[0].url == 'https://docs.example.com'
    assert restored.bookmarks[0].title == 'Docs'
    assert restored.is_blocked('https://ads.example.com/script.js') is True



def test_browser_store_round_trip_snapshot_sqlite(tmp_path: Path) -> None:
    db_path = tmp_path / 'browser.db'
    store = BrowserStore(db_path)

    browser = BrowserModule()
    browser.open_tab('t-1', 'https://example.com', 'Example')
    browser.pin_tab('t-1', True)
    browser.open_tab('t-2', 'https://news.example.com', 'News')
    browser.add_bookmark('https://docs.example.com', 'Docs')
    browser.record_visit('https://docs.example.com', 'Docs')
    browser.add_adblock_rule('ads.')
    browser.queue_download('dl-1', 'https://example.com/file.zip')
    browser.update_download('dl-1', 'completed', '/tmp/file.zip')

    store.save_snapshot(user_id='user-1', browser=browser, workspace_id='ws-1', session_id='session-1')

    restored = store.load_snapshot('user-1')
    assert len(restored.tabs) == 2
    assert restored.tabs[0].is_pinned is True
    assert len(restored.bookmarks) == 1
    assert len(restored.history()) >= 2
    assert restored.downloads[0].status == 'completed'
    assert restored.is_blocked('https://ads.example.com/banner.js') is True



def test_cli_browser_commands_round_trip(tmp_path: Path, monkeypatch, capsys) -> None:
    db_path = tmp_path / 'cli-browser.db'

    monkeypatch.setattr(
        sys,
        'argv',
        ['slate', '--store', str(tmp_path / 'surfaces.json'), 'browser', 'open', 'user-1', 'tab-1', 'https://example.com', '--db', str(db_path)],
    )
    assert main() == 0

    monkeypatch.setattr(
        sys,
        'argv',
        ['slate', '--store', str(tmp_path / 'surfaces.json'), 'browser', 'bookmark', 'user-1', 'https://docs.example.com', '--title', 'Docs', '--db', str(db_path)],
    )
    assert main() == 0

    monkeypatch.setattr(
        sys,
        'argv',
        ['slate', '--store', str(tmp_path / 'surfaces.json'), 'browser', 'list-tabs', 'user-1', '--db', str(db_path)],
    )
    assert main() == 0

    monkeypatch.setattr(
        sys,
        'argv',
        ['slate', '--store', str(tmp_path / 'surfaces.json'), 'browser', 'list-bookmarks', 'user-1', '--db', str(db_path)],
    )
    assert main() == 0

    captured = capsys.readouterr().out
    assert 'tab-1' in captured
    assert 'Docs' in captured



def test_cli_browser_tab_controls_and_downloads(tmp_path: Path, monkeypatch, capsys) -> None:
    db_path = tmp_path / 'cli-browser-controls.db'
    store_path = tmp_path / 'surfaces.json'

    commands = [
        ['slate', '--store', str(store_path), 'browser', 'open', 'user-2', 'tab-a', 'https://a.example', '--db', str(db_path)],
        ['slate', '--store', str(store_path), 'browser', 'open', 'user-2', 'tab-b', 'https://b.example', '--db', str(db_path)],
        ['slate', '--store', str(store_path), 'browser', 'activate', 'user-2', 'tab-b', '--db', str(db_path)],
        ['slate', '--store', str(store_path), 'browser', 'pin', 'user-2', 'tab-b', '--db', str(db_path)],
        ['slate', '--store', str(store_path), 'browser', 'navigate', 'user-2', 'tab-b', 'https://docs.example', '--db', str(db_path)],
        ['slate', '--store', str(store_path), 'browser', 'add-rule', 'user-2', 'ads.', '--db', str(db_path)],
        ['slate', '--store', str(store_path), 'browser', 'download', 'user-2', 'dl-2', 'https://a.example/file.zip', '--db', str(db_path)],
        ['slate', '--store', str(store_path), 'browser', 'download-status', 'user-2', 'dl-2', 'completed', '--saved-path', '/tmp/file.zip', '--db', str(db_path)],
        ['slate', '--store', str(store_path), 'browser', 'list-tabs', 'user-2', '--db', str(db_path)],
        ['slate', '--store', str(store_path), 'browser', 'webview', 'user-2', 'tab-b', '--db', str(db_path)],
        ['slate', '--store', str(store_path), 'browser', 'list-downloads', 'user-2', '--db', str(db_path)],
        ['slate', '--store', str(store_path), 'browser', 'list-rules', 'user-2', '--db', str(db_path)],
        ['slate', '--store', str(store_path), 'browser', 'remove-rule', 'user-2', 'ads.', '--db', str(db_path)],
        ['slate', '--store', str(store_path), 'browser', 'close', 'user-2', 'tab-a', '--db', str(db_path)],
    ]

    for argv in commands:
        monkeypatch.setattr(sys, 'argv', argv)
        assert main() == 0

    output = capsys.readouterr().out
    assert '[pinned]' in output
    assert 'dl-2: completed' in output
    assert 'Closed tab tab-a: True' in output
    assert 'ads.' in output
    assert 'WebView config for tab-b' in output
