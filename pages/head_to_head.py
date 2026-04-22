import dash
from dash import html, dcc, callback, Input, Output
import dash_mantine_components as dmc

from utils.models import (
    get_scores_dataframe,
    get_transfers_dataframe,
    get_team_color_map,
    get_all_teams,
)
from utils.calculations import (
    compute_head_to_head,
    compute_consistency,
    compute_cumulative_points,
    compute_transfer_efficiency,
    compute_power_rankings,
)
from utils.chart_helpers import (
    fig_head_to_head_bars,
    fig_radar_comparison,
    fig_differential,
    empty_fig,
)
from utils.components import section_header, chart_card, create_stat_card, empty_state

dash.register_page(__name__, path="/head-to-head", name="Head-to-Head", order=2)

# ─── Layout ──────────────────────────────────────────────────────────────────

layout = html.Div(
    [
        section_header("Head-to-Head", "Compare two teams side by side"),
        # Team selectors
        html.Div(
            [
                html.Div(
                    dmc.Select(
                        id="h2h-team-a",
                        label="Team A",
                        placeholder="Select Team A",
                        classNames={
                            "input": "form-input-custom",
                            "label": "form-label-custom",
                        },
                        clearable=True,
                        searchable=True,
                    ),
                    className="h2h-select-col",
                ),
                html.Div(
                    html.Div("⚔️", className="h2h-vs"),
                    className="h2h-vs-col",
                ),
                html.Div(
                    dmc.Select(
                        id="h2h-team-b",
                        label="Team B",
                        placeholder="Select Team B",
                        classNames={
                            "input": "form-input-custom",
                            "label": "form-label-custom",
                        },
                        clearable=True,
                        searchable=True,
                    ),
                    className="h2h-select-col",
                ),
            ],
            className="h2h-selector-grid mb-4",
        ),
        # Win record cards
        html.Div(id="h2h-win-record", className="overview-stat-grid mb-4"),
        # Radar + bars
        html.Div(
            [
                html.Div([chart_card("h2h-radar")], className="mb-4"),
                html.Div([chart_card("h2h-bars")], className="mb-4"),
            ],
            className="h2h-chart-grid",
        ),
        # Differential
        html.Div(
            [
                html.Div([chart_card("h2h-differential")], className="mb-4"),
            ],
            className="page-single-column",
        ),
    ],
    className="page-content",
)


# ─── Populate dropdowns ─────────────────────────────────────────────────────


@callback(
    Output("h2h-team-a", "data"),
    Output("h2h-team-b", "data"),
    Input("h2h-team-a", "id"),  # fires once on load
)
def populate_dropdowns(_):
    teams = get_all_teams()
    opts = [{"label": t["name"], "value": t["name"]} for t in teams]
    return opts, opts


# ─── Main update ─────────────────────────────────────────────────────────────


@callback(
    Output("h2h-win-record", "children"),
    Output("h2h-radar", "figure"),
    Output("h2h-bars", "figure"),
    Output("h2h-differential", "figure"),
    Input("h2h-team-a", "value"),
    Input("h2h-team-b", "value"),
)
def update_h2h(team_a, team_b):
    placeholder = empty_fig("Select two teams to compare")
    if not team_a or not team_b or team_a == team_b:
        msg = "Please select two different teams" if team_a == team_b and team_a else ""
        return [], placeholder, placeholder, placeholder

    scores_df = get_scores_dataframe()
    transfers_df = get_transfers_dataframe()
    colors = get_team_color_map()

    if (
        scores_df.empty
        or team_a not in scores_df.columns
        or team_b not in scores_df.columns
    ):
        return [], placeholder, placeholder, placeholder

    # Head-to-head stats
    h2h = compute_head_to_head(scores_df, team_a, team_b)

    # Win record cards
    win_cards = [
        create_stat_card(
            team_a, str(h2h["wins_a"]), "matches won", colors.get(team_a, "#888")
        ),
        create_stat_card("Draws", str(h2h["draws"]), "tied matches", "#888"),
        create_stat_card(
            team_b, str(h2h["wins_b"]), "matches won", colors.get(team_b, "#888")
        ),
        create_stat_card("Matches", str(h2h["matches_played"]), "played", "#4CC9F0"),
    ]

    # Radar chart data
    teams_cols = [c for c in scores_df.columns if c != "Match"]
    cons = compute_consistency(scores_df)
    cons_map = {r["Team"]: r for _, r in cons.iterrows()}

    cum = compute_cumulative_points(scores_df)
    total_a = cum[team_a].iloc[-1] if team_a in cum.columns else 0
    total_b = cum[team_b].iloc[-1] if team_b in cum.columns else 0

    avg_a = cons_map.get(team_a, {}).get("Avg", 0)
    avg_b = cons_map.get(team_b, {}).get("Avg", 0)

    # Lower std dev is better → invert for radar
    max_std = max(
        cons_map.get(team_a, {}).get("Std Dev", 1),
        cons_map.get(team_b, {}).get("Std Dev", 1),
        1,
    )
    consistency_a = max_std - cons_map.get(team_a, {}).get("Std Dev", 0)
    consistency_b = max_std - cons_map.get(team_b, {}).get("Std Dev", 0)

    best_a = scores_df[team_a].max()
    best_b = scores_df[team_b].max()

    pr = compute_power_rankings(scores_df)
    pr_map = {r["Team"]: r["Power Score"] for _, r in pr.iterrows()}
    power_a = pr_map.get(team_a, 0)
    power_b = pr_map.get(team_b, 0)

    eff_df = compute_transfer_efficiency(scores_df, transfers_df)
    eff_a = (
        eff_df[team_a].dropna().iloc[-1]
        if team_a in eff_df.columns and not eff_df[team_a].dropna().empty
        else 0
    )
    eff_b = (
        eff_df[team_b].dropna().iloc[-1]
        if team_b in eff_df.columns and not eff_df[team_b].dropna().empty
        else 0
    )

    stats_a = {
        "Total Pts": total_a,
        "Avg Pts": avg_a,
        "Consistency": consistency_a,
        "Best Match": best_a,
        "Power": power_a,
        "Efficiency": eff_a,
    }
    stats_b = {
        "Total Pts": total_b,
        "Avg Pts": avg_b,
        "Consistency": consistency_b,
        "Best Match": best_b,
        "Power": power_b,
        "Efficiency": eff_b,
    }

    radar_fig = fig_radar_comparison(stats_a, stats_b, team_a, team_b, colors)
    bars_fig = fig_head_to_head_bars(scores_df, team_a, team_b, colors)
    diff_fig = fig_differential(scores_df, team_a, team_b, h2h["diff_series"], colors)

    return win_cards, radar_fig, bars_fig, diff_fig
