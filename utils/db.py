import sqlite3
import os
from utils.constants import DB_PATH


def get_connection():
    """Return a new SQLite connection with row_factory and WAL mode."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_connection()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS teams (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL UNIQUE,
                color       TEXT    NOT NULL,
                abbreviation TEXT   NOT NULL,
                active      INTEGER NOT NULL DEFAULT 1,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS matches (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                match_number INTEGER NOT NULL UNIQUE,
                description  TEXT    DEFAULT '',
                date_played  TEXT    DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS scores (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
                team_id  INTEGER NOT NULL REFERENCES teams(id)   ON DELETE CASCADE,
                points   REAL    NOT NULL DEFAULT 0,
                UNIQUE(match_id, team_id)
            );

            CREATE TABLE IF NOT EXISTS transfers (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
                team_id  INTEGER NOT NULL REFERENCES teams(id)   ON DELETE CASCADE,
                count    INTEGER NOT NULL DEFAULT 0,
                UNIQUE(match_id, team_id)
            );

            CREATE INDEX IF NOT EXISTS idx_scores_match   ON scores(match_id);
            CREATE INDEX IF NOT EXISTS idx_scores_team    ON scores(team_id);
            CREATE INDEX IF NOT EXISTS idx_transfers_match ON transfers(match_id);
            CREATE INDEX IF NOT EXISTS idx_transfers_team  ON transfers(team_id);
        """
        )
        conn.commit()
    finally:
        conn.close()
