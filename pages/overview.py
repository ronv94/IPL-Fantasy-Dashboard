import dash
from dash import html, dcc, callback, Input, Output
import dash_mantine_components as dmc

from utils.constants import TOTAL_MATCHES
from utils.models import (
    get_scores_dataframe,
    get_transfers_dataframe,
    get_team_color_map,
    get_max_match_number,
)
from utils.calculations import compute_leaderboard, compute_cumulative_points
from utils.chart_helpers import fig_points_race, fig_points_earned, empty_fig
from utils.components import (
    create_stat_card,
    section_header,
    chart_card,
    season_progress,
    create_leaderboard,
    empty_state,
)

dash.register_page(__name__, path="/", name="Overview", order=0)

# ─── Layout ──────────────────────────────────────────────────────────────────

layout = html.Div(
    [
        dcc.Interval(id="overview-interval", interval=60_000, n_intervals=0),
        # Season progress
        html.Div(id="overview-progress"),
        # Quick stat cards
        html.Div(id="overview-stat-cards", className="overview-stat-grid mb-4"),
        # Main content: leaderboard + race chart
        html.Div(
            [
                html.Div(
                    [
                        section_header("Leaderboard", "Current standings"),
                        html.Div(id="overview-leaderboard"),
                    ],
                    className="mb-4",
                ),
                html.Div(
                    [
                        section_header(
                            "Points Race", "Cumulative points over the season"
                        ),
                        chart_card("overview-race-chart"),
                    ],
                    className="mb-4",
                ),
            ],
            className="overview-main-grid",
        ),
        # Points per match
        html.Div(
            [
                html.Div(
                    [
                        section_header(
                            "Points Per Match", "Individual match performances"
                        ),
                        chart_card("overview-earned-chart"),
                    ],
                    className="mb-4",
                ),
            ],
            className="page-single-column",
        ),
        # Latest match card
        html.Div(id="overview-latest-match"),
    ],
    className="page-content",
)


# ─── Callbacks ───────────────────────────────────────────────────────────────


@callback(
    Output("overview-progress", "children"),
    Output("overview-stat-cards", "children"),
    Output("overview-leaderboard", "children"),
    Output("overview-race-chart", "figure"),
    Output("overview-earned-chart", "figure"),
    Output("overview-latest-match", "children"),
    Input("overview-interval", "n_intervals"),
)
def update_overview(_n):
    scores_df = get_scores_dataframe()
    colors = get_team_color_map()
    max_match = get_max_match_number()

    # Progress bar
    progress = season_progress(max_match, TOTAL_MATCHES) if max_match > 0 else ""

    if scores_df.empty or len(scores_df.columns) <= 1:
        return (
            progress,
            [],
            empty_state(),
            empty_fig("Enter match scores from the Admin page to see the points race!"),
            empty_fig(),
            "",
        )

    # Leaderboard
    lb = compute_leaderboard(scores_df)
    leaderboard = create_leaderboard(lb, colors)

    # Stat cards
    leader = lb.iloc[0]
    second = lb.iloc[1] if len(lb) > 1 else None
    gap = second["Gap to Leader"] if second is not None else 0

    # Biggest mover
    biggest_mover = lb.loc[lb["Rank Change"].abs().idxmax()]
    mover_dir = (
        "▲"
        if biggest_mover["Rank Change"] > 0
        else "▼" if biggest_mover["Rank Change"] < 0 else "—"
    )

    # Latest match MVP
    teams = [c for c in scores_df.columns if c != "Match"]
    last_row = scores_df.iloc[-1]
    mvp_team = max(
        teams, key=lambda t: last_row[t] if last_row[t] == last_row[t] else 0
    )
    mvp_pts = last_row[mvp_team]

    cards = [
        create_stat_card(
            "👑 Leader",
            leader["Team"],
            f"{leader['Total Points']:,.0f} pts",
            "#FFD23F",
            "",
        ),
        create_stat_card(
            "📏 Gap", f"{gap:,.0f}", f"pts between 1st & 2nd", "#EF476F", ""
        ),
        create_stat_card(
            "🚀 Biggest Mover",
            biggest_mover["Team"],
            f"{mover_dir} {abs(int(biggest_mover['Rank Change']))} spots",
            "#06D6A0",
            "",
        ),
        create_stat_card(
            "⭐ Last MVP",
            mvp_team,
            f"Match {int(last_row['Match'])} — {mvp_pts:,.0f} pts",
            "#4CC9F0",
            "",
        ),
    ]

    # Charts
    cum_df = compute_cumulative_points(scores_df)
    race_fig = fig_points_race(cum_df, colors)
    earned_fig = fig_points_earned(scores_df, colors)

    # Latest match breakdown
    latest_match_card = _build_latest_match(last_row, teams, colors)

    return progress, cards, leaderboard, race_fig, earned_fig, latest_match_card


def _build_latest_match(last_row, teams, colors):
    """Build a card showing all scores for the latest match."""
    match_num = int(last_row["Match"])
    sorted_teams = sorted(
        teams,
        key=lambda t: last_row[t] if last_row[t] == last_row[t] else 0,
        reverse=True,
    )
    mvp = sorted_teams[0]

    rows = []
    for i, t in enumerate(sorted_teams):
        pts = last_row[t]
        is_mvp = i == 0
        rows.append(
            html.Div(
                [
                    html.Span(
                        f"{'⭐ ' if is_mvp else ''}{t}",
                        className="latest-team",
                        style={"color": colors.get(t, "#ccc")},
                    ),
                    html.Span(f"{pts:,.1f}", className="latest-pts"),
                ],
                className=f"latest-row {'latest-mvp' if is_mvp else ''}",
            )
        )

    return dmc.Paper(
        [
            html.H5(f"Match {match_num} Results", className="latest-title"),
            html.Div(rows, className="latest-results"),
        ],
        className="latest-match-card mb-4",
        p="lg",
    )
