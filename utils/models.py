import pandas as pd
from utils.db import get_connection


# ─── Teams ───────────────────────────────────────────────────────────────────


def get_all_teams(active_only=True):
    """Return list of team dicts. If active_only, filter to active=1."""
    conn = get_connection()
    try:
        if active_only:
            rows = conn.execute(
                "SELECT id, name, color, abbreviation, active FROM teams WHERE active=1 ORDER BY name"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, name, color, abbreviation, active FROM teams ORDER BY name"
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_team_color_map():
    """Return {team_name: color_hex} for active teams."""
    teams = get_all_teams()
    return {t["name"]: t["color"] for t in teams}


def add_team(name, color, abbreviation):
    """Insert a new team. Returns the new team id."""
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO teams (name, color, abbreviation) VALUES (?, ?, ?)",
            (name.strip(), color, abbreviation.strip().upper()),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def update_team(team_id, name=None, color=None, abbreviation=None):
    """Update team fields (only non-None values)."""
    conn = get_connection()
    try:
        parts, vals = [], []
        if name is not None:
            parts.append("name=?")
            vals.append(name.strip())
        if color is not None:
            parts.append("color=?")
            vals.append(color)
        if abbreviation is not None:
            parts.append("abbreviation=?")
            vals.append(abbreviation.strip().upper())
        if not parts:
            return
        vals.append(team_id)
        conn.execute(f"UPDATE teams SET {', '.join(parts)} WHERE id=?", vals)
        conn.commit()
    finally:
        conn.close()


def deactivate_team(team_id):
    """Soft-delete: set active=0."""
    conn = get_connection()
    try:
        conn.execute("UPDATE teams SET active=0 WHERE id=?", (team_id,))
        conn.commit()
    finally:
        conn.close()


def reactivate_team(team_id):
    """Re-enable a deactivated team."""
    conn = get_connection()
    try:
        conn.execute("UPDATE teams SET active=1 WHERE id=?", (team_id,))
        conn.commit()
    finally:
        conn.close()


# ─── Matches ─────────────────────────────────────────────────────────────────


def get_all_matches():
    """Return list of match dicts ordered by match_number."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, match_number, team_1, team_2, stadium, date_played FROM matches ORDER BY match_number"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_or_create_match(
    match_number, team_1=None, team_2=None, stadium=None, date_played=None
):
    """Get existing match id or create one, updating metadata when provided."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id FROM matches WHERE match_number=?", (match_number,)
        ).fetchone()
        if row:
            updates = []
            values = []
            for column_name, column_value in (
                ("team_1", team_1),
                ("team_2", team_2),
                ("stadium", stadium),
                ("date_played", date_played),
            ):
                if column_value is not None:
                    updates.append(f"{column_name}=?")
                    values.append(column_value)
            if updates:
                values.append(match_number)
                conn.execute(
                    f"UPDATE matches SET {', '.join(updates)} WHERE match_number=?",
                    values,
                )
                conn.commit()
            return row["id"]
        cur = conn.execute(
            "INSERT INTO matches (match_number, team_1, team_2, stadium, date_played) VALUES (?, ?, ?, ?, ?)",
            (
                match_number,
                team_1 or "",
                team_2 or "",
                stadium or "",
                date_played or "",
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_match_details(match_number):
    """Return match metadata for editing."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT team_1, team_2, stadium, date_played FROM matches WHERE match_number=?",
            (match_number,),
        ).fetchone()
        if not row:
            return {"team_1": "", "team_2": "", "stadium": "", "date_played": ""}
        return dict(row)
    finally:
        conn.close()


def get_max_match_number():
    """Return the highest match_number with data, or 0 if none."""
    conn = get_connection()
    try:
        row = conn.execute("SELECT MAX(match_number) as mx FROM matches").fetchone()
        return row["mx"] or 0
    finally:
        conn.close()


# ─── Scores ──────────────────────────────────────────────────────────────────


def upsert_scores(
    match_number,
    scores_dict,
    team_1=None,
    team_2=None,
    stadium=None,
    date_played=None,
):
    """Insert or update scores for a match.

    scores_dict: {team_name: points_value, ...}
    """
    match_id = get_or_create_match(match_number, team_1, team_2, stadium, date_played)
    conn = get_connection()
    try:
        for team_name, points in scores_dict.items():
            team_row = conn.execute(
                "SELECT id FROM teams WHERE name=? AND active=1", (team_name,)
            ).fetchone()
            if not team_row:
                continue
            conn.execute(
                """INSERT INTO scores (match_id, team_id, points)
                   VALUES (?, ?, ?)
                   ON CONFLICT(match_id, team_id) DO UPDATE SET points=excluded.points""",
                (match_id, team_row["id"], float(points)),
            )
        conn.commit()
    finally:
        conn.close()


# ─── Transfers ───────────────────────────────────────────────────────────────


def upsert_transfers(match_number, transfers_dict):
    """Insert or update transfer counts for a match.

    transfers_dict: {team_name: count, ...}
    """
    match_id = get_or_create_match(match_number)
    conn = get_connection()
    try:
        for team_name, count in transfers_dict.items():
            team_row = conn.execute(
                "SELECT id FROM teams WHERE name=? AND active=1", (team_name,)
            ).fetchone()
            if not team_row:
                continue
            conn.execute(
                """INSERT INTO transfers (match_id, team_id, count)
                   VALUES (?, ?, ?)
                   ON CONFLICT(match_id, team_id) DO UPDATE SET count=excluded.count""",
                (match_id, team_row["id"], int(count)),
            )
        conn.commit()
    finally:
        conn.close()


# ─── DataFrames (pivoted for charts) ────────────────────────────────────────


def get_scores_dataframe():
    """Return DataFrame with columns: Match, Team1, Team2, ...
    Rows = match_numbers, values = points. Sorted by Match.
    """
    conn = get_connection()
    try:
        df = pd.read_sql_query(
            """SELECT m.match_number AS Match, t.name AS team, s.points
               FROM scores s
               JOIN matches m ON s.match_id = m.id
               JOIN teams t   ON s.team_id  = t.id
               WHERE t.active = 1
               ORDER BY m.match_number""",
            conn,
        )
    finally:
        conn.close()
    if df.empty:
        return pd.DataFrame(columns=["Match"])
    return df.pivot(index="Match", columns="team", values="points").reset_index()


def get_transfers_dataframe():
    """Return DataFrame with columns: Match, Team1, Team2, ...
    Rows = match_numbers, values = transfer counts. Sorted by Match.
    """
    conn = get_connection()
    try:
        df = pd.read_sql_query(
            """SELECT m.match_number AS Match, t.name AS team, tr.count AS transfers
               FROM transfers tr
               JOIN matches m ON tr.match_id = m.id
               JOIN teams t   ON tr.team_id  = t.id
               WHERE t.active = 1
               ORDER BY m.match_number""",
            conn,
        )
    finally:
        conn.close()
    if df.empty:
        return pd.DataFrame(columns=["Match"])
    return df.pivot(index="Match", columns="team", values="transfers").reset_index()


# ─── Delete ──────────────────────────────────────────────────────────────────


def delete_match_data(match_number):
    """Delete all scores and transfers for a match, then the match record."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id FROM matches WHERE match_number=?", (match_number,)
        ).fetchone()
        if not row:
            return
        match_id = row["id"]
        conn.execute("DELETE FROM scores WHERE match_id=?", (match_id,))
        conn.execute("DELETE FROM transfers WHERE match_id=?", (match_id,))
        conn.execute("DELETE FROM matches WHERE id=?", (match_id,))
        conn.commit()
    finally:
        conn.close()


def get_match_scores_for_edit(match_number):
    """Return {team_name: points} for a given match for editing."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT t.name, s.points
               FROM scores s
               JOIN matches m ON s.match_id = m.id
               JOIN teams t   ON s.team_id  = t.id
               WHERE m.match_number = ?""",
            (match_number,),
        ).fetchall()
        return {r["name"]: r["points"] for r in rows}
    finally:
        conn.close()


def get_match_transfers_for_edit(match_number):
    """Return {team_name: count} for a given match for editing."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT t.name, tr.count
               FROM transfers tr
               JOIN matches m ON tr.match_id = m.id
               JOIN teams t   ON tr.team_id  = t.id
               WHERE m.match_number = ?""",
            (match_number,),
        ).fetchall()
        return {r["name"]: r["count"] for r in rows}
    finally:
        conn.close()
