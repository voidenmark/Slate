-- Slate database foundation schema (v0)

CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  avatar_url TEXT,
  display_name TEXT,
  created_at INTEGER NOT NULL,
  last_login INTEGER,
  preferences TEXT
);

CREATE TABLE IF NOT EXISTS workspaces (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  name TEXT NOT NULL,
  icon TEXT,
  color TEXT,
  layout TEXT,
  position INTEGER,
  created_at INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS browser_tabs (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  workspace_id TEXT,
  session_id TEXT,
  url TEXT NOT NULL,
  title TEXT,
  favicon_url TEXT,
  is_pinned BOOLEAN DEFAULT 0,
  is_muted BOOLEAN DEFAULT 0,
  parent_tab_id TEXT,
  position INTEGER,
  created_at INTEGER NOT NULL,
  last_accessed INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE SET NULL
);



CREATE TABLE IF NOT EXISTS browser_bookmarks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  url TEXT NOT NULL,
  title TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS browser_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  url TEXT NOT NULL,
  title TEXT NOT NULL,
  visited_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS browser_downloads (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  url TEXT NOT NULL,
  status TEXT NOT NULL,
  saved_path TEXT,
  created_at INTEGER NOT NULL
);



CREATE TABLE IF NOT EXISTS browser_adblock_rules (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  pattern TEXT NOT NULL,
  created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS notes (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  folder_id TEXT,
  title TEXT NOT NULL,
  icon TEXT,
  cover_image TEXT,
  is_public BOOLEAN DEFAULT 0,
  is_archived BOOLEAN DEFAULT 0,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  created_by TEXT NOT NULL,
  updated_by TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS note_blocks (
  id TEXT PRIMARY KEY,
  note_id TEXT NOT NULL,
  type TEXT NOT NULL,
  content TEXT,
  metadata TEXT,
  position INTEGER NOT NULL,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chat_conversations (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  type TEXT NOT NULL,
  name TEXT,
  avatar_url TEXT,
  protocol TEXT NOT NULL,
  external_id TEXT,
  is_archived BOOLEAN DEFAULT 0,
  is_muted BOOLEAN DEFAULT 0,
  folder_id TEXT,
  last_message_at INTEGER,
  created_at INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS emails (
  id TEXT PRIMARY KEY,
  account_id TEXT NOT NULL,
  folder_id TEXT NOT NULL,
  message_id TEXT UNIQUE NOT NULL,
  thread_id TEXT,
  from_address TEXT NOT NULL,
  from_name TEXT,
  to_addresses TEXT NOT NULL,
  subject TEXT,
  body_text TEXT,
  body_html TEXT,
  is_read BOOLEAN DEFAULT 0,
  is_starred BOOLEAN DEFAULT 0,
  category TEXT,
  date INTEGER NOT NULL,
  received_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_browser_tabs_user_last_accessed ON browser_tabs(user_id, last_accessed DESC);
CREATE INDEX IF NOT EXISTS idx_notes_user_updated_at ON notes(user_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_conversations_user_last_message ON chat_conversations(user_id, last_message_at DESC);
CREATE INDEX IF NOT EXISTS idx_emails_thread ON emails(thread_id);

CREATE INDEX IF NOT EXISTS idx_browser_bookmarks_user_created_at ON browser_bookmarks(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_browser_history_user_visited_at ON browser_history(user_id, visited_at DESC);
CREATE INDEX IF NOT EXISTS idx_browser_downloads_user_created_at ON browser_downloads(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_browser_adblock_rules_user_created_at ON browser_adblock_rules(user_id, created_at DESC);
