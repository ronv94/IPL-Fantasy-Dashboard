# Calculations

- Input shape
  - Most functions expect a pivoted pandas DataFrame shaped as: Match | Team A | Team B | ...
  - Team columns are detected by excluding the Match column.
  - Missing team values are usually dropped for per-team stats or filled with 0 for weighted totals, depending on the metric.

- Leaderboard: compute_leaderboard(scores_df)
  - Total Points = sum of every team column across all entered matches.
  - Current Rank = descending order of Total Points.
  - Gap to Leader = leader total minus each team total.
  - Prev Rank = rank using all matches except the latest one; if only one match exists, Prev Rank = current Rank.
  - Rank Change = Prev Rank - Rank.
  - Positive Rank Change means a team moved up the table.

- Cumulative Points: compute_cumulative_points(scores_df)
  - For each team: cumulative total after each match using cumsum().
  - Output preserves the Match column and replaces raw match scores with running totals.

- Consistency: compute_consistency(scores_df)
  - Avg = arithmetic mean of a team's non-null match scores.
  - Std Dev = sample standard deviation of non-null scores via pandas std().
  - CV = coefficient of variation = (Std Dev / Avg) * 100.
  - If Avg <= 0, CV is forced to 0 to avoid divide-by-zero or negative-ratio noise.
  - Min and Max come from the team's non-null match scores.
  - Lower Std Dev ranks higher because results are sorted ascending by Std Dev.

- Streaks: compute_streaks(scores_df)
  - For each match, baseline = average score across all teams in that same match.
  - A team is marked above if its score is strictly greater than that match baseline; otherwise it is treated as below.
  - Current streak is measured backward from the latest match only.
  - Streak Type = "🔥 Hot" for above-average run, "❄️ Cold" for below-average run.
  - If current streak length is below STREAK_MIN_LENGTH, Streak Type is reset to "—".
  - Current threshold: STREAK_MIN_LENGTH = 3.

- Power Rankings: compute_power_rankings(scores_df)
  - Uses exponentially weighted match scores so recent matches matter more.
  - Raw weight for match i = POWER_RANKING_DECAY^(n - 1 - i), where n is the number of matches.
  - Weights are normalized by: weights = weights / weights.sum() * n.
  - Power Score = dot(team_scores_filled_with_0, normalized_weights).
  - Teams are ranked descending by Power Score to get Power Rank.
  - Leaderboard Rank is merged in from compute_leaderboard().
  - Rank Diff = Leaderboard Rank - Power Rank.
  - Positive Rank Diff means recent form is stronger than current table position suggests.
  - Current decay constant: POWER_RANKING_DECAY = 0.92.

- Head-to-Head: compute_head_to_head(scores_df, team_a, team_b)
  - Uses only matches where both teams have recorded values.
  - wins_a = count of matches where team_a > team_b.
  - wins_b = count of matches where team_b > team_a.
  - draws = count of matches where values are equal.
  - matches_played = number of shared non-null match entries.
  - diff_series = cumulative sum of (team_a - team_b) over shared matches.
  - If either team column is missing or the score table is empty, all outputs return zero/empty defaults.

- Rolling Average: compute_rolling_average(scores_df, window=ROLLING_WINDOW)
  - Rolling mean per team using pandas rolling(window, min_periods=1).
  - Early matches use smaller windows until enough matches exist.
  - Values are rounded to 1 decimal place.
  - Default window: ROLLING_WINDOW = 5.

- Transfer Efficiency: compute_transfer_efficiency(scores_df, transfers_df)
  - Uses only teams present in both scores and transfers tables.
  - For each team:
    - cumulative points = cumsum(scores)
    - cumulative transfers = cumsum(transfers with null treated as 0)
    - efficiency = cumulative points / cumulative transfers
  - Zero cumulative transfers are replaced with NaN before division, so efficiency stays blank instead of infinite.
  - Output is a Match-indexed DataFrame of running pts-per-transfer values.

- Awards: compute_awards(scores_df, transfers_df=None)
  - Match MVP Leader
    - For each match, the team with the highest non-null score gets one MVP count.
    - Award goes to every team tied for the highest MVP total, as long as total MVPs > 0.
  - Centurion
    - A team qualifies if it records at least one single-match score >= CENTURION_THRESHOLD.
    - Detail shown is count of qualifying matches and best single-match score.
    - Current threshold: CENTURION_THRESHOLD = 500.
  - Consistency King
    - First compute consistency metrics.
    - Compute each team's total points and the average total across teams.
    - Filter to teams with total points >= average total.
    - Winner = lowest CV among those above-average-total teams.
  - Most Improved
    - Only evaluated when at least 3 matches exist.
    - Early rank = rank from the first entered match only.
    - Final rank = rank from all entered matches.
    - Improvement = early_rank - final_rank.
    - Winner = team with the highest positive climb; no award if the best climb is not positive.
  - Transfer Genius
    - Requires transfer data.
    - Efficiency is based on full-season totals, not rolling efficiency.
    - total efficiency = total points / total transfers, with zero transfers excluded via NaN.
    - Winner = team with highest valid full-season pts-per-transfer.
  - On Fire / Ice Cold
    - Derived from compute_streaks().
    - Only teams whose streak length is at least STREAK_MIN_LENGTH are included.
  - Awards are returned as a dict of badge category -> list of {team, detail}.
  - Empty categories can exist in the raw dict; UI code skips categories with no recipients.

- Form Guide: compute_form_guide(scores_df, n=5)
  - Uses the last n matches only.
  - For each match in that window, baseline = average score across all teams in that match.
  - Each team gets "above" if its score is strictly greater than the baseline; otherwise "below".
  - Equality counts as "below" in the current implementation.
  - Output shape: {team_name: ["above" | "below", ...]}.
  - Default lookback: 5 matches.

- Important implementation details
  - Many comparisons use strict greater-than, not greater-than-or-equal.
  - Several calculations depend on the latest match heavily: Rank Change, Streaks, Form Guide, and page-level MVP summaries.
  - Power ranking fills missing scores with 0 before weighting; consistency and head-to-head usually drop nulls instead.
  - Transfer efficiency intentionally avoids infinite values by converting zero transfers to NaN before division.