"""Reusable Dash UI components."""

from dash import html, dcc
import dash_mantine_components as dmc


# ─── Navbar ──────────────────────────────────────────────────────────────────

NAV_ITEMS = [
    {"label": "Overview", "href": "/"},
    {"label": "Stats", "href": "/stats"},
    {"label": "Head-to-Head", "href": "/head-to-head"},
    {"label": "Power Rankings", "href": "/power-rankings"},
    {"label": "Admin", "href": "/admin"},
]


def create_navbar():
    return dmc.Paper(
        dmc.Flex(
            [
                html.Div(
                    [
                        html.Span("🏏", className="navbar-emoji"),
                        html.Span("IPL Rasiya", className="navbar-brand-text"),
                        html.Span("2026", className="navbar-year"),
                    ],
                    className="navbar-brand-group",
                ),
                html.Div(
                    [
                        dcc.Link(
                            item["label"],
                            href=item["href"],
                            className="nav-link-custom",
                        )
                        for item in NAV_ITEMS
                    ],
                    className="navbar-links",
                ),
            ],
            align="center",
            justify="space-between",
            wrap="wrap",
            className="navbar-shell",
        ),
        className="navbar-custom",
        radius=0,
    )


# ─── Stat Card ───────────────────────────────────────────────────────────────


def create_stat_card(title, value, subtitle="", color="#FF6B35", icon=""):
    return dmc.Paper(
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
        ],
        className="stat-card",
        p="lg",
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
    return dmc.Paper(
        dcc.Graph(id=graph_id, config={"displayModeBar": False}, style=style),
        className="chart-card",
        p="xs",
    )


# ─── Badge Component (for awards) ───────────────────────────────────────────


def create_badge(team, detail, color="#FFD23F"):
    return html.Div(
        [
            html.Div(team, className="badge-team", style={"color": color}),
            html.Div(detail, className="badge-detail"),
        ],
        className="award-badge",
        style={"borderLeftColor": color},
    )


# ─── Form Group ──────────────────────────────────────────────────────────────


def form_field(label, input_id, input_type="number", placeholder="", value=""):
    if input_type == "number":
        input_component = dmc.NumberInput(
            id=input_id,
            value=None if value == "" else value,
            placeholder=placeholder,
            classNames={"input": "form-input-custom", "label": "form-label-custom"},
            hideControls=True,
            label=label,
        )
    else:
        input_component = dmc.TextInput(
            id=input_id,
            value=value,
            placeholder=placeholder,
            classNames={"input": "form-input-custom", "label": "form-label-custom"},
            label=label,
        )

    return html.Div(
        input_component,
        className="form-field-col mb-3",
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
            html.Span(
                f"Season Progress \u2014 Match {current_match} of {total_matches}",
                className="progress-label",
            ),
            html.Span(f"{pct:.0f}%", className="progress-pct"),
        ],
        className="progress-header",
    )


# ─── Leaderboard Row ────────────────────────────────────────────────────────


def leaderboard_row(
    rank,
    team,
    total_points,
    rank_change,
    gap,
    color,
    transfers_used=None,
    total_transfers=None,
    match_score=None,
    is_mvp=False,
):
    if rank_change > 0:
        change_cls, change_text = "rank-up", f"▲{rank_change}"
    elif rank_change < 0:
        change_cls, change_text = "rank-down", f"▼{abs(rank_change)}"
    else:
        change_cls, change_text = "rank-same", "—"

    crown = " 👑" if rank == 1 else ""

    xfers_text = "—"
    if transfers_used is not None and total_transfers is not None:
        remaining = max(total_transfers - int(transfers_used), 0)
        xfers_text = str(remaining)

    match_text, match_cls = "—", "lb-match"
    if match_score is not None:
        match_text = f"⭐ {match_score:,.0f}" if is_mvp else f"{match_score:,.0f}"
        if is_mvp:
            match_cls = "lb-match lb-match-mvp"

    return html.Div(
        [
            html.Span(f"#{rank}", className="lb-rank"),
            html.Div(
                [
                    html.Div(
                        className="lb-color-dot",
                        style={"backgroundColor": color},
                    ),
                    html.Span(f"{team}{crown}", className="lb-team"),
                ],
                className="lb-team-cell",
            ),
            html.Span(match_text, className=match_cls),
            html.Span(f"{total_points:,.0f}", className="lb-points"),
            html.Span(change_text, className=f"lb-change {change_cls}"),
            html.Span(xfers_text, className="lb-xfers"),
        ],
        className=f"lb-row {'lb-row-leader' if rank == 1 else ''}",
    )


def create_leaderboard(
    leaderboard_df, colors, transfers_map=None, total_transfers=None, match_scores=None
):
    """Build the full leaderboard component from leaderboard DataFrame."""
    if leaderboard_df.empty:
        return empty_state("No scores entered yet")

    # Identify MVP (highest scorer in the current match)
    mvp_team = None
    if match_scores:
        valid = {t: s for t, s in match_scores.items() if s is not None}
        if valid:
            mvp_team = max(valid, key=valid.get)

    header = html.Div(
        [
            html.Span("#", className="lb-h"),
            html.Span("Team", className="lb-h"),
            html.Span("Match", className="lb-h lb-h-right"),
            html.Span("Season", className="lb-h lb-h-right"),
            html.Span("±", className="lb-h lb-h-center"),
            html.Span("Xfers left", className="lb-h lb-h-right"),
        ],
        className="lb-header",
    )

    rows = [header]
    for _, r in leaderboard_df.iterrows():
        team = r["Team"]
        used = transfers_map.get(team) if transfers_map else None
        score = match_scores.get(team) if match_scores else None
        rows.append(
            leaderboard_row(
                rank=int(r["Rank"]),
                team=team,
                total_points=r["Total Points"],
                rank_change=int(r["Rank Change"]),
                gap=r["Gap to Leader"],
                color=colors.get(team, "#888"),
                transfers_used=used,
                total_transfers=total_transfers,
                match_score=score,
                is_mvp=(team == mvp_team),
            )
        )
    return html.Div(rows, className="leaderboard")
