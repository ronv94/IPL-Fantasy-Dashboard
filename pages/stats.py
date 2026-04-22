import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

from utils.models import (
    get_scores_dataframe,
    get_transfers_dataframe,
    get_team_color_map,
)
from utils.calculations import (
    compute_consistency,
    compute_rolling_average,
    compute_transfer_efficiency,
)
from utils.chart_helpers import (
    fig_points_distribution,
    fig_scoring_heatmap,
    fig_momentum,
    fig_transfer_efficiency,
    fig_transfers_accumulated,
    fig_transfers_per_match,
    empty_fig,
)
from utils.components import section_header, chart_card, empty_state

dash.register_page(__name__, path="/stats", name="Stats", order=1)

# ─── Layout ──────────────────────────────────────────────────────────────────

layout = html.Div(
    [
        dcc.Interval(id="stats-interval", interval=60_000, n_intervals=0),
        section_header(
            "Stats & Analytics", "Deep dive into scoring patterns and team performance"
        ),
        # Distribution + Heatmap
        dbc.Row(
            [
                dbc.Col(
                    [chart_card("stats-distribution")], lg=6, md=12, className="mb-4"
                ),
                dbc.Col([chart_card("stats-heatmap")], lg=6, md=12, className="mb-4"),
            ]
        ),
        # Consistency table
        section_header(
            "Consistency Leaderboard",
            "Lower standard deviation = more predictable scorer",
        ),
        html.Div(id="stats-consistency-table", className="mb-4"),
        # Rolling average + Transfer efficiency
        dbc.Row(
            [
                dbc.Col(
                    [chart_card("stats-rolling-avg")], lg=6, md=12, className="mb-4"
                ),
                dbc.Col(
                    [chart_card("stats-transfer-eff")], lg=6, md=12, className="mb-4"
                ),
            ]
        ),
        # Transfers
        dbc.Row(
            [
                dbc.Col(
                    [chart_card("stats-transfers-per-match")],
                    lg=6,
                    md=12,
                    className="mb-4",
                ),
                dbc.Col(
                    [chart_card("stats-transfers-accumulated")],
                    lg=6,
                    md=12,
                    className="mb-4",
                ),
            ]
        ),
    ],
    className="page-content",
)


# ─── Callbacks ───────────────────────────────────────────────────────────────


@callback(
    Output("stats-distribution", "figure"),
    Output("stats-heatmap", "figure"),
    Output("stats-consistency-table", "children"),
    Output("stats-rolling-avg", "figure"),
    Output("stats-transfer-eff", "figure"),
    Output("stats-transfers-per-match", "figure"),
    Output("stats-transfers-accumulated", "figure"),
    Input("stats-interval", "n_intervals"),
)
def update_stats(_n):
    scores_df = get_scores_dataframe()
    transfers_df = get_transfers_dataframe()
    colors = get_team_color_map()

    if scores_df.empty or len(scores_df.columns) <= 1:
        e = empty_fig("Enter match scores from the Admin page to see stats!")
        return e, e, empty_state(), e, e, e, e

    # Distribution
    dist_fig = fig_points_distribution(scores_df, colors)

    # Heatmap
    heatmap_fig = fig_scoring_heatmap(scores_df, colors)

    # Consistency table
    cons = compute_consistency(scores_df)
    cons_table = _build_consistency_table(cons, colors)

    # Rolling average
    rolling_df = compute_rolling_average(scores_df)
    rolling_fig = fig_momentum(rolling_df, colors)

    # Transfer efficiency
    eff_df = compute_transfer_efficiency(scores_df, transfers_df)
    eff_fig = fig_transfer_efficiency(eff_df, colors)

    # Transfers
    tr_per_match = (
        fig_transfers_per_match(transfers_df, colors)
        if not transfers_df.empty
        else empty_fig("No transfer data")
    )
    tr_accum = (
        fig_transfers_accumulated(transfers_df, colors)
        if not transfers_df.empty
        else empty_fig("No transfer data")
    )

    return (
        dist_fig,
        heatmap_fig,
        cons_table,
        rolling_fig,
        eff_fig,
        tr_per_match,
        tr_accum,
    )


def _build_consistency_table(cons_df, colors):
    """Build a styled consistency leaderboard."""
    if cons_df.empty:
        return empty_state("Not enough data")

    header = html.Div(
        [
            html.Span("#", className="cons-rank-h"),
            html.Span("Team", className="cons-team-h"),
            html.Span("Avg", className="cons-val-h"),
            html.Span("Std Dev", className="cons-val-h"),
            html.Span("CV%", className="cons-val-h"),
            html.Span("Min", className="cons-val-h"),
            html.Span("Max", className="cons-val-h"),
        ],
        className="cons-header",
    )

    rows = [header]
    for i, r in cons_df.iterrows():
        rows.append(
            html.Div(
                [
                    html.Span(f"{i + 1}", className="cons-rank"),
                    html.Span(
                        r["Team"],
                        className="cons-team",
                        style={"color": colors.get(r["Team"], "#ccc")},
                    ),
                    html.Span(f"{r['Avg']}", className="cons-val"),
                    html.Span(f"{r['Std Dev']}", className="cons-val"),
                    html.Span(f"{r['CV']}%", className="cons-val"),
                    html.Span(f"{r['Min']}", className="cons-val"),
                    html.Span(f"{r['Max']}", className="cons-val"),
                ],
                className="cons-row",
            )
        )

    return html.Div(rows, className="consistency-table")
