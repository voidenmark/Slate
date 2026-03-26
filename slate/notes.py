from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class NoteBlock:
    id: str
    type: str  # e.g., "text", "heading", "image", "code"
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)


@dataclass(slots=True)
class Note:
    id: str
    user_id: str
    title: str
    blocks: list[NoteBlock] = field(default_factory=list)
    folder_id: str | None = None
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)


class NotesModule:
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        self._notes: dict[str, Note] = {}

    def create_note(self, note_id: str, title: str) -> Note:
        if note_id in self._notes:
            raise ValueError(f"Note with id {note_id} already exists.")

        note = Note(id=note_id, user_id=self.user_id, title=title)
        self._notes[note_id] = note
        return note

    def get_note(self, note_id: str) -> Note | None:
        return self._notes.get(note_id)

    def add_block(self, note_id: str, block_id: str, block_type: str, content: str) -> NoteBlock:
        note = self.get_note(note_id)
        if not note:
            raise ValueError(f"Unknown note: {note_id}")

        block = NoteBlock(id=block_id, type=block_type, content=content)
        note.blocks.append(block)
        note.updated_at = _now_iso()
        return block

    def list_notes(self) -> list[Note]:
        return list(self._notes.values())
