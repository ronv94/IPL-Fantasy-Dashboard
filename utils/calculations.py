"""Pure statistical computation functions.

Every function takes pandas DataFrames (pivoted: Match | Team1 | Team2 …)
and returns computed results. No database or Dash dependencies.
"""

import numpy as np
import pandas as pd
from utils.constants import (
    CENTURION_THRESHOLD,
    STREAK_MIN_LENGTH,
    ROLLING_WINDOW,
    POWER_RANKING_DECAY,
)


def _team_cols(df):
    """Return column names that are team names (everything except 'Match')."""
    return [c for c in df.columns if c != "Match"]


# ─── Leaderboard ─────────────────────────────────────────────────────────────


def compute_leaderboard(scores_df):
    """Compute current leaderboard from raw scores.

    Returns DataFrame with columns:
        Rank, Team, Total Points, Prev Rank, Rank Change, Gap to Leader
    """
    if scores_df.empty or len(scores_df) == 0:
        return pd.DataFrame(
            columns=[
                "Rank",
                "Team",
                "Total Points",
                "Prev Rank",
                "Rank Change",
                "Gap to Leader",
            ]
        )

    teams = _team_cols(scores_df)
    totals = scores_df[teams].sum().reset_index()
    totals.columns = ["Team", "Total Points"]
    totals = totals.sort_values("Total Points", ascending=False).reset_index(drop=True)
    totals["Rank"] = range(1, len(totals) + 1)
    totals["Gap to Leader"] = totals["Total Points"].iloc[0] - totals["Total Points"]

    # Previous rank (all matches except last)
    if len(scores_df) > 1:
        prev = scores_df.iloc[:-1]
        prev_totals = prev[teams].sum().reset_index()
        prev_totals.columns = ["Team", "Prev Total"]
        prev_totals = prev_totals.sort_values(
            "Prev Total", ascending=False
        ).reset_index(drop=True)
        prev_totals["Prev Rank"] = range(1, len(prev_totals) + 1)
        totals = totals.merge(prev_totals[["Team", "Prev Rank"]], on="Team", how="left")
    else:
        totals["Prev Rank"] = totals["Rank"]

    totals["Rank Change"] = totals["Prev Rank"] - totals["Rank"]
    return totals[
        ["Rank", "Team", "Total Points", "Prev Rank", "Rank Change", "Gap to Leader"]
    ]


# ─── Cumulative Points ──────────────────────────────────────────────────────


def compute_cumulative_points(scores_df):
    """Return DataFrame with cumulative sums: Match | Team1_cum | Team2_cum ..."""
    if scores_df.empty:
        return scores_df.copy()
    teams = _team_cols(scores_df)
    result = scores_df[["Match"]].copy()
    for t in teams:
        result[t] = scores_df[t].cumsum()
    return result


# ─── Consistency ─────────────────────────────────────────────────────────────


def compute_consistency(scores_df):
    """Return DataFrame: Team, Avg, Std Dev, CV (coefficient of variation), Min, Max."""
    if scores_df.empty:
        return pd.DataFrame(columns=["Team", "Avg", "Std Dev", "CV", "Min", "Max"])
    teams = _team_cols(scores_df)
    rows = []
    for t in teams:
        s = scores_df[t].dropna()
        avg = s.mean()
        std = s.std()
        rows.append(
            {
                "Team": t,
                "Avg": round(avg, 1),
                "Std Dev": round(std, 1),
                "CV": round(std / avg * 100, 1) if avg > 0 else 0,
                "Min": round(s.min(), 1),
                "Max": round(s.max(), 1),
            }
        )
    return pd.DataFrame(rows).sort_values("Std Dev").reset_index(drop=True)


# ─── Streaks ─────────────────────────────────────────────────────────────────


def compute_streaks(scores_df):
    """Compute hot/cold streaks for each team.

    A streak is consecutive matches above (hot) or below (cold) the overall
    match average. Returns DataFrame: Team, Streak Type, Streak Length.
    """
    if scores_df.empty:
        return pd.DataFrame(columns=["Team", "Streak Type", "Streak Length"])
    teams = _team_cols(scores_df)
    rows = []
    for t in teams:
        s = scores_df[t].dropna()
        if len(s) == 0:
            rows.append({"Team": t, "Streak Type": "—", "Streak Length": 0})
            continue
        match_avgs = scores_df[teams].mean(axis=1)
        above = (s.values > match_avgs.values).astype(int)

        # Walk backwards to find current streak
        if len(above) == 0:
            rows.append({"Team": t, "Streak Type": "—", "Streak Length": 0})
            continue
        streak_val = above[-1]
        streak_len = 0
        for i in range(len(above) - 1, -1, -1):
            if above[i] == streak_val:
                streak_len += 1
            else:
                break
        streak_type = "🔥 Hot" if streak_val == 1 else "❄️ Cold"
        if streak_len < STREAK_MIN_LENGTH:
            streak_type = "—"
        rows.append(
            {"Team": t, "Streak Type": streak_type, "Streak Length": streak_len}
        )
    return pd.DataFrame(rows)


# ─── Power Rankings ──────────────────────────────────────────────────────────


def compute_power_rankings(scores_df):
    """Exponentially weighted rankings — recent matches count more.

    Returns DataFrame: Team, Power Score, Power Rank, Leaderboard Rank, Rank Diff
    """
    if scores_df.empty:
        return pd.DataFrame(
            columns=[
                "Team",
                "Power Score",
                "Power Rank",
                "Leaderboard Rank",
                "Rank Diff",
            ]
        )
    teams = _team_cols(scores_df)
    n = len(scores_df)
    weights = np.array([POWER_RANKING_DECAY ** (n - 1 - i) for i in range(n)])
    weights = weights / weights.sum() * n  # normalize so sum ≈ n

    rows = []
    for t in teams:
        vals = scores_df[t].fillna(0).values
        power = float(np.dot(vals, weights))
        rows.append({"Team": t, "Power Score": round(power, 1)})
    pr = (
        pd.DataFrame(rows)
        .sort_values("Power Score", ascending=False)
        .reset_index(drop=True)
    )
    pr["Power Rank"] = range(1, len(pr) + 1)

    # Leaderboard rank for comparison
    lb = compute_leaderboard(scores_df)
    pr = pr.merge(
        lb[["Team", "Rank"]].rename(columns={"Rank": "Leaderboard Rank"}), on="Team"
    )
    pr["Rank Diff"] = pr["Leaderboard Rank"] - pr["Power Rank"]
    return pr


# ─── Head-to-Head ────────────────────────────────────────────────────────────


def compute_head_to_head(scores_df, team_a, team_b):
    """Compare two teams match-by-match.

    Returns dict with:
        wins_a, wins_b, draws, matches_played,
        diff_series (pd.Series of cumulative difference A-B)
    """
    if (
        scores_df.empty
        or team_a not in scores_df.columns
        or team_b not in scores_df.columns
    ):
        return {
            "wins_a": 0,
            "wins_b": 0,
            "draws": 0,
            "matches_played": 0,
            "diff_series": pd.Series(dtype=float),
        }

    a = scores_df[team_a].dropna()
    b = scores_df[team_b].dropna()
    common = a.index.intersection(b.index)
    a, b = a.loc[common], b.loc[common]

    wins_a = int((a > b).sum())
    wins_b = int((b > a).sum())
    draws = int((a == b).sum())
    diff = (a - b).cumsum()

    return {
        "wins_a": wins_a,
        "wins_b": wins_b,
        "draws": draws,
        "matches_played": len(common),
        "diff_series": diff,
    }


# ─── Rolling Average ────────────────────────────────────────────────────────


def compute_rolling_average(scores_df, window=ROLLING_WINDOW):
    """Return DataFrame with rolling mean: Match | Team1 | Team2 ..."""
    if scores_df.empty:
        return scores_df.copy()
    teams = _team_cols(scores_df)
    result = scores_df[["Match"]].copy()
    for t in teams:
        result[t] = scores_df[t].rolling(window=window, min_periods=1).mean().round(1)
    return result


# ─── Transfer Efficiency ────────────────────────────────────────────────────


def compute_transfer_efficiency(scores_df, transfers_df):
    """Cumulative points / cumulative transfers over the season.

    Returns DataFrame: Match | Team1 | Team2 … (efficiency values)
    """
    if scores_df.empty or transfers_df.empty:
        return pd.DataFrame(columns=["Match"])
    teams = _team_cols(scores_df)
    common_teams = [t for t in teams if t in transfers_df.columns]
    result = scores_df[["Match"]].copy()
    for t in common_teams:
        cum_pts = scores_df[t].cumsum()
        cum_tr = transfers_df[t].fillna(0).cumsum()
        eff = cum_pts / cum_tr.replace(0, np.nan)
        result[t] = eff.round(1)
    return result


# ─── Awards / Badges ────────────────────────────────────────────────────────


def compute_awards(scores_df, transfers_df=None):
    """Compute season awards.

    Returns dict:  { badge_name: [ {team, detail}, ... ] }
    """
    awards = {}
    if scores_df.empty:
        return awards
    teams = _team_cols(scores_df)

    # --- Match MVPs (highest scorer each match) ---
    mvp_counts = {t: 0 for t in teams}
    for _, row in scores_df.iterrows():
        vals = {t: row[t] for t in teams if pd.notna(row[t])}
        if vals:
            mvp = max(vals, key=vals.get)
            mvp_counts[mvp] += 1
    most_mvps = max(mvp_counts.values()) if mvp_counts else 0
    awards["🏆 Match MVP Leader"] = [
        {"team": t, "detail": f"{c} MVPs"}
        for t, c in sorted(mvp_counts.items(), key=lambda x: -x[1])
        if c == most_mvps and c > 0
    ]

    # --- Centurion (500+ single match) ---
    centurions = []
    for t in teams:
        big = scores_df[scores_df[t] >= CENTURION_THRESHOLD]
        if len(big) > 0:
            centurions.append(
                {"team": t, "detail": f"{len(big)}× ({int(scores_df[t].max())} best)"}
            )
    awards["💎 Centurion"] = centurions

    # --- Consistency King (lowest CV with above-avg total) ---
    cons = compute_consistency(scores_df)
    totals = scores_df[teams].sum()
    avg_total = totals.mean()
    above_avg = cons[cons["Team"].isin(totals[totals >= avg_total].index)]
    if not above_avg.empty:
        best = above_avg.sort_values("CV").iloc[0]
        awards["🏅 Consistency King"] = [
            {"team": best["Team"], "detail": f"CV: {best['CV']}%"}
        ]

    # --- Most Improved (biggest rank climb first match → last) ---
    if len(scores_df) >= 3:
        early = scores_df.iloc[:1]
        early_rank = early[teams].sum().rank(ascending=False)
        final_rank = scores_df[teams].sum().rank(ascending=False)
        improvement = early_rank - final_rank
        best_team = improvement.idxmax()
        climb = int(improvement[best_team])
        if climb > 0:
            awards["📈 Most Improved"] = [
                {"team": best_team, "detail": f"Climbed {climb} spots"}
            ]

    # --- Transfer Genius (best cumulative efficiency at latest match) ---
    if transfers_df is not None and not transfers_df.empty:
        common = [t for t in teams if t in transfers_df.columns]
        if common:
            total_pts = scores_df[common].sum()
            total_tr = transfers_df[common].fillna(0).sum()
            eff = total_pts / total_tr.replace(0, np.nan)
            eff = eff.dropna()
            if not eff.empty:
                best_t = eff.idxmax()
                awards["🎯 Transfer Genius"] = [
                    {"team": best_t, "detail": f"{eff[best_t]:.1f} pts/transfer"}
                ]

    # --- On Fire / Ice Cold (current streaks) ---
    streaks = compute_streaks(scores_df)
    hot = streaks[
        (streaks["Streak Type"] == "🔥 Hot")
        & (streaks["Streak Length"] >= STREAK_MIN_LENGTH)
    ]
    cold = streaks[
        (streaks["Streak Type"] == "❄️ Cold")
        & (streaks["Streak Length"] >= STREAK_MIN_LENGTH)
    ]
    if not hot.empty:
        awards["🔥 On Fire"] = [
            {"team": r["Team"], "detail": f"{r['Streak Length']} match streak"}
            for _, r in hot.iterrows()
        ]
    if not cold.empty:
        awards["❄️ Ice Cold"] = [
            {"team": r["Team"], "detail": f"{r['Streak Length']} match streak"}
            for _, r in cold.iterrows()
        ]

    return awards


# ─── Form Guide (last N matches) ────────────────────────────────────────────


def compute_form_guide(scores_df, n=5):
    """Return dict of {team: list of 'above'/'below'} for last n matches."""
    if scores_df.empty:
        return {}
    teams = _team_cols(scores_df)
    last_n = scores_df.tail(n)
    match_avgs = last_n[teams].mean(axis=1)
    guide = {}
    for t in teams:
        vals = last_n[t].values
        avgs = match_avgs.values
        guide[t] = ["above" if v > a else "below" for v, a in zip(vals, avgs)]
    return guide
