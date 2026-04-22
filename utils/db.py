import sqlite3
import os
from utils.constants import DB_PATH
from utils.fixtures import IPL_2026_MATCHES


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
                team_1       TEXT    DEFAULT '',
                team_2       TEXT    DEFAULT '',
                stadium      TEXT    DEFAULT '',
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
        _migrate_matches_table(conn)
        _seed_matches_table(conn)
        conn.commit()
    finally:
        conn.close()


def _migrate_matches_table(conn):
    """Migrate the matches table to the current metadata schema."""
    columns = {
        row["name"] for row in conn.execute("PRAGMA table_info(matches)").fetchall()
    }

    if not columns:
        return

    for column_name in ("team_1", "team_2", "stadium"):
        if column_name not in columns:
            conn.execute(
                f"ALTER TABLE matches ADD COLUMN {column_name} TEXT DEFAULT ''"
            )

    if "Team 1" in columns:
        conn.execute(
            """
            UPDATE matches
            SET team_1 = CASE
                WHEN COALESCE(team_1, '') = '' THEN "Team 1"
                ELSE team_1
            END
            """
        )
        conn.execute('ALTER TABLE matches DROP COLUMN "Team 1"')

    if "Team 2" in columns:
        conn.execute(
            """
            UPDATE matches
            SET team_2 = CASE
                WHEN COALESCE(team_2, '') = '' THEN "Team 2"
                ELSE team_2
            END
            """
        )
        conn.execute('ALTER TABLE matches DROP COLUMN "Team 2"')

    if "home" in columns:
        conn.execute(
            """
            UPDATE matches
            SET team_1 = CASE
                WHEN COALESCE(team_1, '') = '' THEN home
                ELSE team_1
            END
            """
        )
        conn.execute("ALTER TABLE matches DROP COLUMN home")

    if "away" in columns:
        conn.execute(
            """
            UPDATE matches
            SET team_2 = CASE
                WHEN COALESCE(team_2, '') = '' THEN away
                ELSE team_2
            END
            """
        )
        conn.execute("ALTER TABLE matches DROP COLUMN away")

    if "description" in columns:
        conn.execute("ALTER TABLE matches DROP COLUMN description")


def _seed_matches_table(conn):
    """Insert the IPL 2026 fixture list without overwriting existing metadata."""
    conn.executemany(
        """
        INSERT INTO matches (match_number, team_1, team_2, stadium, date_played)
        VALUES (:match_number, :team_1, :team_2, :stadium, :date_played)
        ON CONFLICT(match_number) DO UPDATE SET
            team_1 = CASE WHEN COALESCE(matches.team_1, '') = '' THEN excluded.team_1 ELSE matches.team_1 END,
            team_2 = CASE WHEN COALESCE(matches.team_2, '') = '' THEN excluded.team_2 ELSE matches.team_2 END,
            stadium = CASE WHEN COALESCE(matches.stadium, '') = '' THEN excluded.stadium ELSE matches.stadium END,
            date_played = CASE WHEN COALESCE(matches.date_played, '') = '' THEN excluded.date_played ELSE matches.date_played END
        """,
        IPL_2026_MATCHES,
    )
