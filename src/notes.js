/**
 * Notes module foundations for Phase 3.
 */

export class NoteBlock {
  /**
   * @param {{ id: string, type: string, content: string, metadata?: Object, createdAt?: string, updatedAt?: string }} input
   */
  constructor(input) {
    if (!input?.id || !input?.type) {
      throw new Error('NoteBlock requires both id and type.');
    }

    this.id = input.id;
    this.type = input.type;
    this.content = input.content ?? '';
    this.metadata = input.metadata ?? {};
    this.createdAt = input.createdAt ?? new Date().toISOString();
    this.updatedAt = input.updatedAt ?? new Date().toISOString();
  }

  toJSON() {
    return {
      id: this.id,
      type: this.type,
      content: this.content,
      metadata: this.metadata,
      createdAt: this.createdAt,
      updatedAt: this.updatedAt
    };
  }
}

export class Note {
  /**
   * @param {{ id: string, userId: string, title: string, blocks?: Array<NoteBlock>, folderId?: string, createdAt?: string, updatedAt?: string }} input
   */
  constructor(input) {
    if (!input?.id || !input?.userId || !input?.title) {
      throw new Error('Note requires id, userId, and title.');
    }

    this.id = input.id;
    this.userId = input.userId;
    this.title = input.title;
    this.blocks = (input.blocks ?? []).map((block) => new NoteBlock(block));
    this.folderId = input.folderId ?? null;
    this.createdAt = input.createdAt ?? new Date().toISOString();
    this.updatedAt = input.updatedAt ?? new Date().toISOString();
  }

  toJSON() {
    return {
      id: this.id,
      userId: this.userId,
      title: this.title,
      blocks: this.blocks.map((block) => block.toJSON()),
      folderId: this.folderId,
      createdAt: this.createdAt,
      updatedAt: this.updatedAt
    };
  }
}

export class NotesModule {
  constructor(userId) {
    this.userId = userId;
    /** @type {Map<string, Note>} */
    this.notes = new Map();
  }

  createNote(noteId, title) {
    if (this.notes.has(noteId)) {
      throw new Error(`Note with id "${noteId}" already exists.`);
    }

    const note = new Note({ id: noteId, userId: this.userId, title });
    this.notes.set(noteId, note);
    return note;
  }

  getNote(noteId) {
    return this.notes.get(noteId);
  }

  addBlock(noteId, blockId, type, content) {
    const note = this.getNote(noteId);
    if (!note) {
      throw new Error(`Unknown note: ${noteId}`);
    }

    const block = new NoteBlock({ id: blockId, type, content });
    note.blocks.push(block);
    note.updatedAt = new Date().toISOString();
    return block;
  }

  listNotes() {
    return [...this.notes.values()].sort((a, b) => b.updatedAt.localeCompare(a.updatedAt));
  }
}
