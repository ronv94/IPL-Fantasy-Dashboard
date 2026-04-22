# Page Behavior

- Overview page (/)
  - Auto-refreshes every 60 seconds via dcc.Interval.
  - Shows season progress only when at least one match exists.
  - Empty state: leaderboard placeholder plus empty charts when no scores are entered.
  - Builds four top cards: current leader, gap between 1st and 2nd, biggest mover by rank change, and latest match MVP.
  - Main visuals: cumulative points race and per-match points earned.
  - Latest match card sorts teams by most recent match score and highlights the top scorer with a star.

- Stats page (/stats)
  - Auto-refreshes every 60 seconds via dcc.Interval.
  - Empty state: all charts return placeholder figures until score data exists.
  - Main analytics: score distribution, scoring heatmap, rolling average momentum, transfer efficiency.
  - Includes a consistency leaderboard table with avg, std dev, coefficient of variation, min, and max.
  - Transfer charts render only when transfer data exists; otherwise show "No transfer data".

- Head-to-Head page (/head-to-head)
  - Team dropdowns are populated from active teams on load.
  - Requires two different teams; identical or missing selection returns placeholder figures.
  - Win record cards show wins for team A, draws, wins for team B, and matches played.
  - Radar comparison combines total points, average points, inverted consistency, best match, power score, and latest transfer-efficiency value.
  - Bar chart compares direct match results between the two teams.
  - Differential chart shows per-match margin trend from compute_head_to_head().

- Power Rankings page (/power-rankings)
  - Auto-refreshes every 60 seconds via dcc.Interval.
  - Empty state: placeholders for table, form, streaks, momentum, and awards until score data exists.
  - Power table compares power rank vs leaderboard rank and shows rank diff arrows.
  - Form guide renders the last five matches as above/below-average blocks per team.
  - Streaks panel only shows active streaks; otherwise displays "No active streaks right now".
  - Momentum chart uses 5-match rolling averages.
  - Awards section groups badge-style recognitions from compute_awards(); hidden categories with no recipients are skipped.

- Admin page (/admin)
  - Open access; no auth gate.
  - Team management lets users add teams with name, abbreviation, and palette color.
  - Team list includes deactivate/reactivate controls; deactivation is soft-delete through active flag.
  - Score entry section generates one numeric input per active team and can load existing values for a selected match.
  - Saving scores requires a match number and at least one entered score; writes through upsert_scores().
  - Transfer entry mirrors score entry with integer inputs and optional load-existing flow.
  - Saving transfers requires a match number and at least one entered value; writes through upsert_transfers().
  - Danger zone deletes all score/transfer data for a selected match via delete_match_data().
  - Summary card updates after team, score, transfer, or delete actions and shows active team count, entered matches, and latest match number.

- Shared behavior across analytic pages
  - Most read-only pages pull fresh DataFrames from utils/models.py inside callbacks rather than caching state in the client.
  - Team colors come from the active team color map and are reused across cards, tables, and charts.
  - Empty or low-data states are intentional and handled with empty_state() or empty_fig() instead of broken visuals.