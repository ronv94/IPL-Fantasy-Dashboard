import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

from utils.models import (
    get_scores_dataframe,
    get_transfers_dataframe,
    get_team_color_map,
)
from utils.calculations import (
    compute_power_rankings,
    compute_streaks,
    compute_form_guide,
    compute_rolling_average,
    compute_awards,
)
from utils.chart_helpers import fig_momentum, empty_fig
from utils.components import section_header, chart_card, create_badge, empty_state

dash.register_page(__name__, path="/power-rankings", name="Power Rankings", order=3)

# ─── Layout ──────────────────────────────────────────────────────────────────

layout = html.Div(
    [
        dcc.Interval(id="pr-interval", interval=60_000, n_intervals=0),
        section_header(
            "Power Rankings",
            "Weighted by recent form — who's peaking at the right time?",
        ),
        # Power rankings table
        html.Div(id="pr-table", className="mb-4"),
        # Form guide + Streaks
        dbc.Row(
            [
                dbc.Col(
                    [
                        section_header(
                            "Form Guide",
                            "Last 5 matches: green = above average, red = below",
                        ),
                        html.Div(id="pr-form-guide"),
                    ],
                    lg=6,
                    md=12,
                    className="mb-4",
                ),
                dbc.Col(
                    [
                        section_header("Current Streaks", "Hot and cold runs"),
                        html.Div(id="pr-streaks"),
                    ],
                    lg=6,
                    md=12,
                    className="mb-4",
                ),
            ]
        ),
        # Momentum chart
        section_header("Momentum", "5-match rolling average — see who's trending up"),
        chart_card("pr-momentum"),
        html.Div(className="mb-4"),
        # Awards
        section_header("Season Awards 🏆", "Bragging rights earned on the field"),
        html.Div(id="pr-awards", className="mb-4"),
    ],
    className="page-content",
)


# ─── Callbacks ───────────────────────────────────────────────────────────────


@callback(
    Output("pr-table", "children"),
    Output("pr-form-guide", "children"),
    Output("pr-streaks", "children"),
    Output("pr-momentum", "figure"),
    Output("pr-awards", "children"),
    Input("pr-interval", "n_intervals"),
)
def update_power_rankings(_n):
    scores_df = get_scores_dataframe()
    transfers_df = get_transfers_dataframe()
    colors = get_team_color_map()

    if scores_df.empty or len(scores_df.columns) <= 1:
        return (
            empty_state(),
            empty_state("Not enough data for form guide"),
            empty_state("Not enough data for streaks"),
            empty_fig("Enter match scores to see momentum trends!"),
            empty_state("Awards will appear as the season progresses"),
        )

    # Power rankings table
    pr = compute_power_rankings(scores_df)
    pr_table = _build_power_table(pr, colors)

    # Form guide
    form = compute_form_guide(scores_df)
    form_guide = _build_form_guide(form, colors)

    # Streaks
    streaks = compute_streaks(scores_df)
    streaks_ui = _build_streaks(streaks, colors)

    # Momentum chart
    rolling_df = compute_rolling_average(scores_df)
    momentum_fig = fig_momentum(rolling_df, colors)

    # Awards
    awards = compute_awards(scores_df, transfers_df)
    awards_ui = _build_awards(awards, colors)

    return pr_table, form_guide, streaks_ui, momentum_fig, awards_ui


# ─── Helper builders ────────────────────────────────────────────────────────


def _build_power_table(pr_df, colors):
    header = html.Div(
        [
            html.Span("#", className="pr-rank-h"),
            html.Span("Team", className="pr-team-h"),
            html.Span("Power Score", className="pr-val-h"),
            html.Span("LB Rank", className="pr-val-h"),
            html.Span("Diff", className="pr-val-h"),
        ],
        className="pr-header",
    )

    rows = [header]
    for _, r in pr_df.iterrows():
        diff = int(r["Rank Diff"])
        if diff > 0:
            diff_text = f"▲ {diff}"
            diff_cls = "rank-up"
        elif diff < 0:
            diff_text = f"▼ {abs(diff)}"
            diff_cls = "rank-down"
        else:
            diff_text = "—"
            diff_cls = "rank-same"

        rows.append(
            html.Div(
                [
                    html.Span(f"{int(r['Power Rank'])}", className="pr-rank"),
                    html.Span(
                        r["Team"],
                        className="pr-team",
                        style={"color": colors.get(r["Team"], "#ccc")},
                    ),
                    html.Span(f"{r['Power Score']:,.0f}", className="pr-val"),
                    html.Span(f"#{int(r['Leaderboard Rank'])}", className="pr-val"),
                    html.Span(diff_text, className=f"pr-val {diff_cls}"),
                ],
                className="pr-row",
            )
        )

    return html.Div(rows, className="power-table")


def _build_form_guide(form_dict, colors):
    if not form_dict:
        return empty_state("Not enough data")
    rows = []
    for team, results in form_dict.items():
        blocks = []
        for r in results:
            cls = "form-block-above" if r == "above" else "form-block-below"
            blocks.append(html.Div(className=f"form-block {cls}"))
        rows.append(
            html.Div(
                [
                    html.Span(
                        team,
                        className="form-team",
                        style={"color": colors.get(team, "#ccc")},
                    ),
                    html.Div(blocks, className="form-blocks"),
                ],
                className="form-row",
            )
        )
    return html.Div(rows, className="form-guide")


def _build_streaks(streaks_df, colors):
    if streaks_df.empty:
        return empty_state("Not enough data")
    active = streaks_df[streaks_df["Streak Type"] != "—"].sort_values(
        "Streak Length", ascending=False
    )
    if active.empty:
        return html.P("No active streaks right now", className="text-muted")
    rows = []
    for _, r in active.iterrows():
        rows.append(
            html.Div(
                [
                    html.Span(r["Streak Type"], className="streak-type"),
                    html.Span(
                        r["Team"],
                        className="streak-team",
                        style={"color": colors.get(r["Team"], "#ccc")},
                    ),
                    html.Span(f"{r['Streak Length']} matches", className="streak-len"),
                ],
                className="streak-row",
            )
        )
    return html.Div(rows, className="streaks-list")


def _build_awards(awards_dict, colors):
    if not awards_dict:
        return empty_state("Awards will appear as the season unfolds")
    sections = []
    for badge_name, recipients in awards_dict.items():
        if not recipients:
            continue
        badges = []
        for r in recipients:
            color = colors.get(r["team"], "#FFD23F")
            icon = badge_name.split(" ")[0]  # emoji
            badges.append(create_badge(icon, r["team"], r["detail"], color))
        sections.append(
            html.Div(
                [
                    html.H6(badge_name, className="award-category"),
                    html.Div(badges, className="award-badges"),
                ],
                className="award-section",
            )
        )
    return html.Div(sections, className="awards-container")
