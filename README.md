# Slate

One Surface for Everything.

## Foundation Added

This repository now includes a first-pass technical foundation for SLATE:

- `src/types/modules.ts`: canonical module list and module metadata.
- `src/core/moduleRegistry.ts`: lightweight in-memory module registry for enable/disable and lookup.
- `src/state/appState.ts`: initial app state model and state transition helpers.
- `db/schema.sql`: SQLite starter schema for identity, workspaces, browser tabs, notes, chat conversations, and emails.

## Next Steps

- Wire app state into a UI shell (Electron + React).
- Add persistence layer to connect `appState` and module configuration to SQLite.
- Implement IPC boundaries for main/renderer separation.
