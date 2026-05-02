"""Plotly figure factory functions.

Every function returns a go.Figure with consistent theming.
"""

import numpy as np
import plotly.graph_objects as go
from utils.constants import CHART_LAYOUT_DEFAULTS, CHART_HEIGHT


def _apply_theme(fig, title="", **overrides):
    """Apply standard layout theme to a figure."""
    layout = {
        **CHART_LAYOUT_DEFAULTS,
        "title": dict(
            text=title,
            font=dict(size=15),
            x=0.0,
            xanchor="left",
            pad=dict(l=4, t=2),
        ),
    }
    layout.update(overrides)
    fig.update_layout(**layout)
    return fig


def _team_cols(df):
    return [c for c in df.columns if c != "Match"]


def empty_fig(message="No data available yet"):
    """Return a placeholder figure with a message."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=18, color="#888"),
    )
    return _apply_theme(fig)


# ─── Points Race (Cumulative Line Chart) ────────────────────────────────────


def fig_points_race(cumulative_df, colors):
    """Cumulative points line chart over matches."""
    if cumulative_df.empty:
        return empty_fig()
    fig = go.Figure()
    teams = _team_cols(cumulative_df)
    for t in teams:
        fig.add_trace(
            go.Scatter(
                x=cumulative_df["Match"],
                y=cumulative_df[t],
                mode="lines",
                name=t,
                line=dict(color=colors.get(t, "#888"), width=3, shape="spline"),
                hovertemplate=f"<b>{t}</b><br>Match %{{x}}<br>Total: %{{y:,.0f}} pts<extra></extra>",
            )
        )
    return _apply_theme(
        fig, title="", xaxis_title="Match", yaxis_title="Cumulative Points"
    )


# ─── Points Earned Per Match (Scatter) ───────────────────────────────────────


def fig_points_earned(scores_df, colors):
    """Bubble scatter of points earned per match."""
    if scores_df.empty:
        return empty_fig()
    fig = go.Figure()
    teams = _team_cols(scores_df)
    for t in teams:
        size = (
            scores_df[t].clip(lower=50) / scores_df[t].max() * 18
            if scores_df[t].max() > 0
            else 6
        )
        fig.add_trace(
            go.Scatter(
                x=scores_df["Match"],
                y=scores_df[t],
                mode="markers",
                name=t,
                marker=dict(
                    color=colors.get(t, "#888"),
                    size=size,
                    opacity=0.8,
                    line=dict(width=1, color="rgba(255,255,255,0.3)"),
                ),
                hovertemplate=f"<b>{t}</b><br>Match %{{x}}<br>Points: %{{y:,.1f}}<extra></extra>",
            )
        )
    return _apply_theme(fig, title="", xaxis_title="Match", yaxis_title="Points")


# ─── Points Distribution (Box Plot) ─────────────────────────────────────────


def fig_points_distribution(scores_df, colors):
    """Box plot showing score distribution per team."""
    if scores_df.empty:
        return empty_fig()
    fig = go.Figure()
    teams = _team_cols(scores_df)
    totals = {t: scores_df[t].sum() for t in teams}
    sorted_teams = sorted(teams, key=lambda x: totals[x], reverse=True)
    for t in sorted_teams:
        fig.add_trace(
            go.Box(
                y=scores_df[t].dropna(),
                name=t,
                marker_color=colors.get(t, "#888"),
                boxmean="sd",
                hoverinfo="y+name",
            )
        )
    return _apply_theme(
        fig, title="Score Distribution", yaxis_title="Points", showlegend=False
    )


# ─── Scoring Heatmap ────────────────────────────────────────────────────────


def fig_scoring_heatmap(scores_df, colors):
    """Heatmap: rows = teams, cols = matches, color = points."""
    if scores_df.empty:
        return empty_fig()
    teams = _team_cols(scores_df)
    totals = {t: scores_df[t].sum() for t in teams}
    sorted_teams = sorted(teams, key=lambda x: totals[x], reverse=True)
    z = [scores_df[t].values for t in sorted_teams]
    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=scores_df["Match"].values,
            y=sorted_teams,
            colorscale="YlOrRd",
            hovertemplate="Match %{x}<br>%{y}<br>Points: %{z:,.0f}<extra></extra>",
        )
    )
    return _apply_theme(
        fig,
        title="Scoring Heatmap",
        xaxis_title="Match",
        height=max(CHART_HEIGHT, len(teams) * 45 + 100),
    )


# ─── Head-to-Head Bars ──────────────────────────────────────────────────────


def fig_head_to_head_bars(scores_df, team_a, team_b, colors):
    """Grouped bar chart comparing two teams match by match."""
    if (
        scores_df.empty
        or team_a not in scores_df.columns
        or team_b not in scores_df.columns
    ):
        return empty_fig("Select two teams to compare")
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=scores_df["Match"],
            y=scores_df[team_a],
            name=team_a,
            marker_color=colors.get(team_a, "#888"),
            opacity=0.9,
        )
    )
    fig.add_trace(
        go.Bar(
            x=scores_df["Match"],
            y=scores_df[team_b],
            name=team_b,
            marker_color=colors.get(team_b, "#888"),
            opacity=0.9,
        )
    )
    return _apply_theme(
        fig,
        title=f"{team_a}  vs  {team_b}",
        barmode="group",
        xaxis_title="Match",
        yaxis_title="Points",
    )


# ─── Radar Comparison ────────────────────────────────────────────────────────


def fig_radar_comparison(stats_a, stats_b, team_a, team_b, colors):
    """Radar chart comparing two teams across multiple metrics.

    stats_a / stats_b: dict with keys matching categories.
    """
    categories = list(stats_a.keys())
    if not categories:
        return empty_fig("Not enough data for radar comparison")

    # Normalize to 0-100 scale
    vals_a = list(stats_a.values())
    vals_b = list(stats_b.values())
    max_vals = [max(abs(a), abs(b), 1) for a, b in zip(vals_a, vals_b)]
    norm_a = [a / m * 100 for a, m in zip(vals_a, max_vals)]
    norm_b = [b / m * 100 for b, m in zip(vals_b, max_vals)]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=norm_a + [norm_a[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name=team_a,
            line=dict(color=colors.get(team_a, "#888"), width=2),
            opacity=0.7,
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=norm_b + [norm_b[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name=team_b,
            line=dict(color=colors.get(team_b, "#888"), width=2),
            opacity=0.7,
        )
    )
    return _apply_theme(
        fig,
        title=f"{team_a}  vs  {team_b}",
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True, showticklabels=False, gridcolor="rgba(255,255,255,0.1)"
            ),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        ),
    )


# ─── Differential Chart ─────────────────────────────────────────────────────


def fig_differential(scores_df, team_a, team_b, diff_series, colors):
    """Area chart of cumulative points difference (A − B)."""
    if diff_series.empty:
        return empty_fig("Select two teams to compare")
    matches = scores_df["Match"].iloc[diff_series.index]
    fig = go.Figure()
    positive = diff_series.clip(lower=0)
    negative = diff_series.clip(upper=0)
    fig.add_trace(
        go.Scatter(
            x=matches,
            y=positive,
            fill="tozeroy",
            name=f"{team_a} leads",
            line=dict(color=colors.get(team_a, "#888"), width=1),
            fillcolor=colors.get(team_a, "#888") + "55",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=matches,
            y=negative,
            fill="tozeroy",
            name=f"{team_b} leads",
            line=dict(color=colors.get(team_b, "#888"), width=1),
            fillcolor=colors.get(team_b, "#888") + "55",
        )
    )
    return _apply_theme(
        fig,
        title="Cumulative Points Differential",
        xaxis_title="Match",
        yaxis_title="Points Diff (cumulative)",
    )


# ─── Momentum (Rolling Average) ─────────────────────────────────────────────


def fig_momentum(rolling_df, colors):
    """Rolling average line chart."""
    if rolling_df.empty:
        return empty_fig()
    fig = go.Figure()
    teams = _team_cols(rolling_df)
    for t in teams:
        fig.add_trace(
            go.Scatter(
                x=rolling_df["Match"],
                y=rolling_df[t],
                mode="lines",
                name=t,
                line=dict(color=colors.get(t, "#888"), width=2.5, shape="spline"),
                hovertemplate=f"<b>{t}</b><br>Match %{{x}}<br>Rolling Avg: %{{y:,.1f}}<extra></extra>",
            )
        )
    return _apply_theme(
        fig,
        title="Momentum (5-Match Rolling Avg)",
        xaxis_title="Match",
        yaxis_title="Rolling Avg Points",
    )


# ─── Transfer Efficiency ────────────────────────────────────────────────────


def fig_transfer_efficiency(efficiency_df, colors):
    """Cumulative points per transfer over the season."""
    if efficiency_df.empty:
        return empty_fig()
    fig = go.Figure()
    teams = _team_cols(efficiency_df)
    for t in teams:
        fig.add_trace(
            go.Scatter(
                x=efficiency_df["Match"],
                y=efficiency_df[t],
                mode="lines",
                name=t,
                line=dict(color=colors.get(t, "#888"), width=2.5, shape="spline"),
                hovertemplate=f"<b>{t}</b><br>Match %{{x}}<br>Efficiency: %{{y:,.1f}}<extra></extra>",
            )
        )
    return _apply_theme(
        fig,
        title="Transfer Efficiency (Pts / Transfer)",
        xaxis_title="Match",
        yaxis_title="Points per Transfer",
    )


# ─── Transfers Accumulated ──────────────────────────────────────────────────


def fig_transfers_accumulated(transfers_df, colors):
    """Cumulative transfers line chart."""
    if transfers_df.empty:
        return empty_fig()
    fig = go.Figure()
    teams = _team_cols(transfers_df)
    cum = transfers_df.copy()
    for t in teams:
        cum[t] = transfers_df[t].fillna(0).cumsum()
        fig.add_trace(
            go.Scatter(
                x=cum["Match"],
                y=cum[t],
                mode="lines",
                name=t,
                line=dict(color=colors.get(t, "#888"), width=2.5, shape="spline"),
                hovertemplate=f"<b>{t}</b><br>Match %{{x}}<br>Total Transfers: %{{y:.0f}}<extra></extra>",
            )
        )
    return _apply_theme(
        fig,
        title="Accumulated Transfers",
        xaxis_title="Match",
        yaxis_title="Total Transfers",
    )


# ─── Transfers Per Match (Scatter) ──────────────────────────────────────────


def fig_transfers_per_match(transfers_df, colors):
    """Scatter plot of transfer counts per match."""
    if transfers_df.empty:
        return empty_fig()
    fig = go.Figure()
    teams = _team_cols(transfers_df)
    for t in teams:
        fig.add_trace(
            go.Scatter(
                x=transfers_df["Match"],
                y=transfers_df[t],
                mode="markers",
                name=t,
                marker=dict(color=colors.get(t, "#888"), size=8, opacity=0.8),
                hovertemplate=f"<b>{t}</b><br>Match %{{x}}<br>Transfers: %{{y}}<extra></extra>",
            )
        )
    return _apply_theme(
        fig,
        title="Transfers Per Match",
        xaxis_title="Match",
        yaxis_title="Transfers",
        yaxis=dict(dtick=1, gridcolor="rgba(255,255,255,0.08)"),
    )
