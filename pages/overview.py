import dash
from dash import html, dcc, callback, Input, Output
import dash_mantine_components as dmc

from utils.constants import TOTAL_MATCHES, TOTAL_TRANSFERS
from utils.models import (
    get_scores_dataframe,
    get_transfers_dataframe,
    get_team_color_map,
    get_max_match_number,
    get_match_details,
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


# ─── Fixture helpers (shared with admin) ────────────────────────────────────

IPL_TEAM_ALIASES = {
    "CHENNAI SUPER KINGS": "CSK",
    "CSK": "CSK",
    "DELHI CAPITALS": "DC",
    "DC": "DC",
    "GUJARAT TITANS": "GT",
    "GT": "GT",
    "KOLKATA KNIGHT RIDERS": "KKR",
    "KKR": "KKR",
    "LUCKNOW SUPER GIANTS": "LSG",
    "LSG": "LSG",
    "MUMBAI INDIANS": "MI",
    "MI": "MI",
    "PUNJAB KINGS": "PBKS",
    "PBKS": "PBKS",
    "RAJASTHAN ROYALS": "RR",
    "RR": "RR",
    "ROYAL CHALLENGERS BENGALURU": "RCB",
    "ROYAL CHALLENGERS BANGALORE": "RCB",
    "RCB": "RCB",
    "SUNRISERS HYDERABAD": "SRH",
    "SRH": "SRH",
}


def _normalize_ipl_team(team_name):
    if not team_name:
        return "TBD", "TBD"
    display_name = str(team_name).strip()
    abbreviation = IPL_TEAM_ALIASES.get(display_name.upper(), display_name.upper())
    return display_name, abbreviation


def _format_match_date(date_value):
    from datetime import datetime

    if not date_value:
        return "Date TBD"
    try:
        return datetime.strptime(str(date_value), "%Y-%m-%d").strftime("%b %d, %Y")
    except ValueError:
        return str(date_value)


def _team_logo_src(team_abbr):
    if not team_abbr:
        return None
    _, abbreviation = _normalize_ipl_team(team_abbr)
    return dash.get_asset_url(f"images/ipl-teams/{abbreviation.strip().lower()}.png")


def _build_overview_fixture(match_number):
    """Admin-style fixture card with logos, match info, date and stadium."""
    details = get_match_details(int(match_number))
    t1_name, t1_abbr = _normalize_ipl_team(details.get("team_1"))
    t2_name, t2_abbr = _normalize_ipl_team(details.get("team_2"))
    stadium = details.get("stadium") or "Stadium TBD"
    match_date = _format_match_date(details.get("date_played"))

    def team_badge(name, abbr):
        logo_src = _team_logo_src(abbr)
        logo = (
            html.Img(src=logo_src, alt=name, className="ov-fix-logo")
            if logo_src
            else html.Div(abbr[:3], className="ov-fix-logo ov-fix-logo-fallback")
        )
        return html.Div(
            [logo, html.Span(abbr, className="ov-fix-code")],
            className="ov-fix-badge",
        )

    return html.Div(
        [
            # Header row: match pill + date
            html.Div(
                [
                    html.Span(
                        f"Match {int(match_number)}",
                        className="admin-match-number-pill",
                    ),
                    html.Span(match_date, className="ov-fix-date"),
                ],
                className="ov-fix-header",
            ),
            # Team badges
            html.Div(
                [
                    team_badge(t1_name, t1_abbr),
                    html.Span("vs", className="ov-fix-vs"),
                    team_badge(t2_name, t2_abbr),
                ],
                className="ov-fix-matchup",
            ),
            # Stadium
            html.Span(stadium, className="ov-fix-stadium"),
        ],
        className="ov-fix-card",
    )


def _slider_marks():
    mark_values = [1] + list(range(10, TOTAL_MATCHES + 1, 10))
    if TOTAL_MATCHES not in mark_values:
        mark_values.append(TOTAL_MATCHES)
    return [{"value": v, "label": str(v)} for v in mark_values]


# ─── Layout ──────────────────────────────────────────────────────────────────


def layout():
    max_match = get_max_match_number()
    initial = max_match if max_match > 0 else TOTAL_MATCHES

    return html.Div(
        [
            dcc.Interval(id="overview-interval", interval=60_000, n_intervals=0),
            # ── Hero: fixture (left) + slider & stat cards (right) ─────────
            html.Div(
                [
                    # Left column: fixture card
                    html.Div(
                        id="overview-match-fixture",
                        className="ov-hero-fixture",
                    ),
                    # Right column: progress, slider, stat cards
                    html.Div(
                        [
                            html.Div(
                                id="overview-stat-cards",
                                className="overview-stat-grid",
                            ),
                            html.Div(id="overview-progress"),
                            dmc.Slider(
                                id="overview-match-slider",
                                value=initial,
                                min=1,
                                max=TOTAL_MATCHES,
                                marks=_slider_marks(),
                                color="orange",
                                size="lg",
                                radius="xl",
                                showLabelOnHover=True,
                                className="season-progress-slider",
                            ),
                        ],
                        className="ov-hero-right",
                    ),
                ],
                className="ov-hero mb-2",
            ),
            # ── Main: leaderboard (left) + stacked charts (right) ──────────
            html.Div(
                [
                    html.Div(
                        [
                            section_header("Leaderboard", "Current standings"),
                            html.Div(id="overview-leaderboard"),
                        ],
                        className="overview-leaderboard-col",
                    ),
                    html.Div(
                        dmc.Tabs(
                            [
                                dmc.TabsList(
                                    [
                                        dmc.TabsTab("Points Race", value="race"),
                                        dmc.TabsTab("Points Per Match", value="earned"),
                                    ],
                                    className="ov-chart-tabs-list",
                                ),
                                dmc.TabsPanel(
                                    chart_card("overview-race-chart"),
                                    value="race",
                                ),
                                dmc.TabsPanel(
                                    chart_card("overview-earned-chart"),
                                    value="earned",
                                ),
                            ],
                            value="race",
                            color="orange",
                            variant="pills",
                            className="ov-chart-tabs",
                        ),
                        className="ov-charts-col",
                    ),
                ],
                className="overview-main-grid",
            ),
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
    Input("overview-interval", "n_intervals"),
    Input("overview-match-slider", "value"),
)
def update_overview(_n, selected_match):
    scores_df = get_scores_dataframe()
    colors = get_team_color_map()
    max_match = get_max_match_number()

    selected_match = int(selected_match) if selected_match else (max_match or 1)

    # Filter scores up to the selected match
    if not scores_df.empty and "Match" in scores_df.columns:
        scores_df = scores_df[scores_df["Match"] <= selected_match]

    # Progress header
    display_match = selected_match if selected_match > 0 else max_match
    progress = (
        season_progress(display_match, TOTAL_MATCHES) if display_match > 0 else ""
    )

    if scores_df.empty or len(scores_df.columns) <= 1:
        return (
            progress,
            [],
            empty_state(),
            empty_fig("Enter match scores from the Admin page to see the points race!"),
            empty_fig(),
        )

    # Leaderboard
    lb = compute_leaderboard(scores_df)
    transfers_df = get_transfers_dataframe()
    # Filter transfers to match selection window
    if not transfers_df.empty and "Match" in transfers_df.columns:
        transfers_df = transfers_df[transfers_df["Match"] <= selected_match]
    team_cols = (
        [c for c in transfers_df.columns if c != "Match"]
        if not transfers_df.empty
        else []
    )
    transfers_map = (
        {t: int(transfers_df[t].fillna(0).sum()) for t in team_cols}
        if team_cols
        else None
    )
    # Build match scores dict for the last visible match
    teams = [c for c in scores_df.columns if c != "Match"]
    last_row = scores_df.iloc[-1]
    match_scores = {
        t: last_row[t] if last_row[t] == last_row[t] else None for t in teams
    }
    leaderboard = create_leaderboard(
        lb,
        colors,
        transfers_map=transfers_map,
        total_transfers=TOTAL_TRANSFERS,
        match_scores=match_scores,
    )

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

    # Latest match MVP (from match_scores)
    mvp_team = max(
        (t for t in match_scores if match_scores[t] is not None),
        key=lambda t: match_scores[t],
        default=None,
    )
    mvp_pts = match_scores[mvp_team] if mvp_team else 0

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

    return progress, cards, leaderboard, race_fig, earned_fig


@callback(
    Output("overview-match-fixture", "children"),
    Input("overview-match-slider", "value"),
)
def update_overview_fixture(selected_match):
    if not selected_match:
        return ""
    return _build_overview_fixture(int(selected_match))
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
