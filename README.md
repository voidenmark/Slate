# Slate

One Surface for Everything.

Built by **VOIDENMARK**.

## Current state

This repository now includes a lightweight domain model and delivery plan scaffolding for building Slate in eight phases.

### Implemented foundation pieces

- Surface and Slate in-memory domain model with ranked universal search.
- Module and app-state primitives for a multi-module desktop shell.
- SQLite schema and Python database initialization helper.
- Delivery roadmap constants and execution progress helpers for tracking an 18-week phased plan.
- Phase 2 browser foundations: tab management, navigation, history/bookmarks, ad-block rule matching, download queue state, and webview config scaffolding.
- Phase 2 browser checkpoint includes JS/Python state serialization for restoring browser sessions.
- Phase 2 now includes SQLite-backed browser snapshot persistence (tabs, bookmarks, history, downloads).

## Delivery phases

1. **Foundation (Weeks 1-2)**
   - Project setup and folder structure
   - Database initialization
   - Core architecture (IPC, state management)
   - Basic layout with three columns
   - Universal search shell
2. **Browser Module (Weeks 3-4)**
   - Tab management
   - WebView integration
   - Bookmarks & history
   - Ad blocking
   - Downloads
3. **Notes Module (Weeks 5-6)**
   - TipTap/BlockNote editor
   - Rich text blocks
   - Folder organization
   - Database tables (Notion-like)
4. **Communication (Weeks 7-8)**
   - Email (IMAP/SMTP)
   - AI categorization
   - Multi-protocol chat (WhatsApp, Discord)
   - Unified messaging
5. **Media (Weeks 9-10)**
   - YouTube integration
   - Video player with PiP
   - Spotify/music player
   - Podcast RSS feeds
6. **Code & Work (Weeks 11-14)**
   - Monaco editor
   - Terminal integration
   - Git operations
   - Kanban boards
   - Calendar sync
7. **Advanced Features (Weeks 15-16)**
   - Finance (Plaid)
   - Design tools
   - AI Assistant (Claude)
   - Extension system
8. **Polish & Optimization (Weeks 17-18)**
   - Performance tuning
   - Memory leak fixes
   - UI polish
   - Accessibility

## Quick start

```bash
npm test
pytest
slate roadmap
slate status
```
