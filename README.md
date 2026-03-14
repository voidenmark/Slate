# Slate

One Surface for Everything.

## Current state

This repository now includes a lightweight domain model for managing surfaces:

- `Surface`: a single unit of content (dashboard, note, board, etc.)
- `Slate`: an in-memory surface collection with indexing helpers

## Capabilities

- Add and list surfaces with strict id uniqueness
- Filter surfaces by tag
- Search surfaces with lightweight relevance ranking
  - exact title matches outrank prefix/substring matches
  - optional `tag`, `kind`, and result `limit` filters

## Quick start

```bash
npm test
```

## Next steps

- Persistence adapters (JSON/file/db)
- Sync and collaboration primitives
