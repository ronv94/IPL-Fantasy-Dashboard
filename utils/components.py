"""Reusable Dash UI components."""

from dash import html, dcc
import dash_bootstrap_components as dbc


# ─── Navbar ──────────────────────────────────────────────────────────────────

NAV_ITEMS = [
    {"label": "Overview", "href": "/"},
    {"label": "Stats", "href": "/stats"},
    {"label": "Head-to-Head", "href": "/head-to-head"},
    {"label": "Power Rankings", "href": "/power-rankings"},
    {"label": "Admin", "href": "/admin"},
]


def create_navbar():
    return dbc.Navbar(
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    html.Span("🏏", className="navbar-emoji"),
                                    html.Span(
                                        "IPL Rasiya", className="navbar-brand-text"
                                    ),
                                    html.Span("2026", className="navbar-year"),
                                ],
                                className="navbar-brand-group",
                            ),
                            width="auto",
                        ),
                        dbc.Col(
                            dbc.Nav(
                                [
                                    dbc.NavItem(
                                        dbc.NavLink(
                                            item["label"],
                                            href=item["href"],
                                            className="nav-link-custom",
                                        )
                                    )
                                    for item in NAV_ITEMS
                                ],
                                navbar=True,
                                className="ms-auto",
                            ),
                        ),
                    ],
                    align="center",
                    className="w-100",
                ),
            ],
            fluid=True,
        ),
        className="navbar-custom",
        dark=True,
    )


# ─── Stat Card ───────────────────────────────────────────────────────────────


def create_stat_card(title, value, subtitle="", color="#FF6B35", icon=""):
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.Span(icon, className="stat-card-icon") if icon else None,
                        html.H6(title, className="stat-card-title"),
                    ],
                    className="stat-card-header",
                ),
                html.H3(value, className="stat-card-value", style={"color": color}),
                html.P(subtitle, className="stat-card-subtitle") if subtitle else None,
            ]
        ),
        className="stat-card",
    )


# ─── Section Header ─────────────────────────────────────────────────────────


def section_header(title, subtitle=""):
    return html.Div(
        [
            html.H4(title, className="section-title"),
            html.P(subtitle, className="section-subtitle") if subtitle else None,
        ],
        className="section-header",
    )


# ─── Chart Card (wraps a dcc.Graph in a styled card) ────────────────────────


def chart_card(graph_id, height=None):
    style = {"height": height} if height else {}
    return dbc.Card(
        dcc.Graph(id=graph_id, config={"displayModeBar": False}, style=style),
        className="chart-card",
    )


# ─── Badge Component (for awards) ───────────────────────────────────────────


def create_badge(icon, team, detail, color="#FFD23F"):
    return html.Div(
        [
            html.Span(icon, className="badge-icon"),
            html.Div(
                [
                    html.Strong(team, style={"color": color}),
                    html.Span(f"  —  {detail}", className="badge-detail"),
                ],
                className="badge-text",
            ),
        ],
        className="award-badge",
    )


# ─── Form Group ──────────────────────────────────────────────────────────────


def form_field(label, input_id, input_type="number", placeholder="", value=""):
    return dbc.Col(
        [
            dbc.Label(label, className="form-label-custom"),
            dbc.Input(
                id=input_id,
                type=input_type,
                placeholder=placeholder,
                value=value,
                className="form-input-custom",
            ),
        ],
        md=4,
        sm=6,
        xs=12,
        className="mb-3",
    )


# ─── Empty State ─────────────────────────────────────────────────────────────


def empty_state(
    message="No data yet. Head to Admin to add teams and enter match scores!",
):
    return html.Div(
        [
            html.Div("🏏", className="empty-state-icon"),
            html.P(message, className="empty-state-text"),
        ],
        className="empty-state",
    )


# ─── Season Progress Bar ────────────────────────────────────────────────────


def season_progress(current_match, total_matches):
    pct = current_match / total_matches * 100
    return html.Div(
        [
            html.Div(
                [
                    html.Span(
                        f"Match {current_match} of {total_matches}",
                        className="progress-label",
                    ),
                    html.Span(f"{pct:.0f}%", className="progress-pct"),
                ],
                className="progress-header",
            ),
            dbc.Progress(
                value=pct,
                className="season-progress",
                color="warning" if pct < 50 else "success",
            ),
        ],
        className="progress-wrapper",
    )


# ─── Leaderboard Row ────────────────────────────────────────────────────────


def leaderboard_row(rank, team, total_points, rank_change, gap, color):
    if rank_change > 0:
        change_cls = "rank-up"
        change_text = f"▲ {rank_change}"
    elif rank_change < 0:
        change_cls = "rank-down"
        change_text = f"▼ {abs(rank_change)}"
    else:
        change_cls = "rank-same"
        change_text = "—"

    crown = " 👑" if rank == 1 else ""

    return html.Div(
        [
            html.Div(
                [
                    html.Span(f"#{rank}", className="lb-rank"),
                    html.Div(
                        className="lb-color-dot", style={"backgroundColor": color}
                    ),
                    html.Span(f"{team}{crown}", className="lb-team"),
                ],
                className="lb-left",
            ),
            html.Div(
                [
                    html.Span(f"{total_points:,.1f}", className="lb-points"),
                    html.Span(change_text, className=f"lb-change {change_cls}"),
                    html.Span(f"-{gap:,.0f}" if gap > 0 else "", className="lb-gap"),
                ],
                className="lb-right",
            ),
        ],
        className=f"lb-row {'lb-row-leader' if rank == 1 else ''}",
    )


def create_leaderboard(leaderboard_df, colors):
    """Build the full leaderboard component from leaderboard DataFrame."""
    if leaderboard_df.empty:
        return empty_state("No scores entered yet")
    rows = []
    for _, r in leaderboard_df.iterrows():
        rows.append(
            leaderboard_row(
                rank=int(r["Rank"]),
                team=r["Team"],
                total_points=r["Total Points"],
                rank_change=int(r["Rank Change"]),
                gap=r["Gap to Leader"],
                color=colors.get(r["Team"], "#888"),
            )
        )
    return html.Div(rows, className="leaderboard")
