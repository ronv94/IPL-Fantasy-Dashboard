import dash
from dash import html, dcc, callback, Input, Output, State, ctx, ALL, no_update
import dash_bootstrap_components as dbc

from utils.constants import TEAM_COLORS, TOTAL_MATCHES
from utils.models import (
    get_all_teams,
    add_team,
    deactivate_team,
    reactivate_team,
    upsert_scores,
    upsert_transfers,
    get_match_scores_for_edit,
    get_match_transfers_for_edit,
    delete_match_data,
    get_max_match_number,
    get_all_matches,
    get_match_details,
)
from utils.components import section_header, form_field

dash.register_page(__name__, path="/admin", name="Admin", order=4)

# ─── Layout ──────────────────────────────────────────────────────────────────

layout = html.Div(
    [
        html.Div(
            id="admin-panel",
            children=[
                section_header("Admin Panel", "Manage teams, enter match data"),
                # ── Team Management ──
                dbc.Card(
                    [
                        dbc.CardHeader(html.H5("Team Management", className="mb-0")),
                        dbc.CardBody(
                            [
                                dbc.Row(
                                    [
                                        form_field(
                                            "Team Name",
                                            "admin-team-name",
                                            "text",
                                            "e.g. Thunder Kings",
                                        ),
                                        form_field(
                                            "Abbreviation",
                                            "admin-team-abbr",
                                            "text",
                                            "e.g. TK",
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label(
                                                    "Color",
                                                    className="form-label-custom",
                                                ),
                                                dcc.Dropdown(
                                                    id="admin-team-color",
                                                    options=[
                                                        {
                                                            "label": html.Span(
                                                                [
                                                                    html.Div(
                                                                        style={
                                                                            "width": "16px",
                                                                            "height": "16px",
                                                                            "backgroundColor": c,
                                                                            "display": "inline-block",
                                                                            "borderRadius": "3px",
                                                                            "marginRight": "8px",
                                                                            "verticalAlign": "middle",
                                                                        }
                                                                    ),
                                                                    c,
                                                                ]
                                                            ),
                                                            "value": c,
                                                        }
                                                        for c in TEAM_COLORS
                                                    ],
                                                    placeholder="Pick a color",
                                                    className="dropdown-dark",
                                                ),
                                            ],
                                            md=4,
                                            sm=6,
                                            xs=12,
                                            className="mb-3",
                                        ),
                                    ]
                                ),
                                dbc.Button(
                                    "Add Team",
                                    id="admin-add-team-btn",
                                    color="success",
                                    className="me-2",
                                ),
                                html.Div(id="admin-team-msg", className="mt-2"),
                                html.Hr(),
                                html.H6("Active Teams"),
                                html.Div(id="admin-teams-list"),
                            ]
                        ),
                    ],
                    className="admin-card mb-4",
                ),
                # ── Enter Match Scores ──
                dbc.Card(
                    [
                        dbc.CardHeader(html.H5("Enter Match Scores", className="mb-0")),
                        dbc.CardBody(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Label(
                                                    "Match Number",
                                                    className="form-label-custom",
                                                ),
                                                dbc.Input(
                                                    id="admin-match-number",
                                                    type="number",
                                                    min=1,
                                                    max=TOTAL_MATCHES,
                                                    placeholder="e.g. 1",
                                                    className="form-input-custom",
                                                ),
                                            ],
                                            md=3,
                                            className="mb-3",
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label(
                                                    "Team 1",
                                                    className="form-label-custom",
                                                ),
                                                dbc.Input(
                                                    id="admin-match-team-1",
                                                    type="text",
                                                    placeholder="e.g. MI",
                                                    className="form-input-custom",
                                                ),
                                            ],
                                            md=2,
                                            className="mb-3",
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label(
                                                    "Team 2",
                                                    className="form-label-custom",
                                                ),
                                                dbc.Input(
                                                    id="admin-match-team-2",
                                                    type="text",
                                                    placeholder="e.g. CSK",
                                                    className="form-input-custom",
                                                ),
                                            ],
                                            md=2,
                                            className="mb-3",
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label(
                                                    "Stadium",
                                                    className="form-label-custom",
                                                ),
                                                dbc.Input(
                                                    id="admin-match-stadium",
                                                    type="text",
                                                    placeholder="e.g. Wankhede Stadium",
                                                    className="form-input-custom",
                                                ),
                                            ],
                                            md=3,
                                            className="mb-3",
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Button(
                                                    "Load Existing",
                                                    id="admin-load-match-btn",
                                                    color="info",
                                                    className="mt-4",
                                                ),
                                            ],
                                            md=2,
                                            className="mb-3",
                                        ),
                                    ]
                                ),
                                html.Div(id="admin-score-fields"),
                                dbc.Button(
                                    "Save Scores",
                                    id="admin-save-scores-btn",
                                    color="success",
                                    className="me-2 mt-2",
                                ),
                                html.Div(id="admin-scores-msg", className="mt-2"),
                            ]
                        ),
                    ],
                    className="admin-card mb-4",
                ),
                # ── Enter Transfers ──
                dbc.Card(
                    [
                        dbc.CardHeader(html.H5("Enter Transfers", className="mb-0")),
                        dbc.CardBody(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Label(
                                                    "Match Number",
                                                    className="form-label-custom",
                                                ),
                                                dbc.Input(
                                                    id="admin-transfer-match",
                                                    type="number",
                                                    min=1,
                                                    max=TOTAL_MATCHES,
                                                    placeholder="e.g. 1",
                                                    className="form-input-custom",
                                                ),
                                            ],
                                            md=3,
                                            className="mb-3",
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Button(
                                                    "Load Existing",
                                                    id="admin-load-transfer-btn",
                                                    color="info",
                                                    className="mt-4",
                                                ),
                                            ],
                                            md=2,
                                            className="mb-3",
                                        ),
                                    ]
                                ),
                                html.Div(id="admin-transfer-fields"),
                                dbc.Button(
                                    "Save Transfers",
                                    id="admin-save-transfers-btn",
                                    color="success",
                                    className="me-2 mt-2",
                                ),
                                html.Div(id="admin-transfers-msg", className="mt-2"),
                            ]
                        ),
                    ],
                    className="admin-card mb-4",
                ),
                # ── Danger Zone ──
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H5("⚠️ Danger Zone", className="mb-0 text-danger")
                        ),
                        dbc.CardBody(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Label(
                                                    "Match # to delete",
                                                    className="form-label-custom",
                                                ),
                                                dbc.Input(
                                                    id="admin-delete-match",
                                                    type="number",
                                                    min=1,
                                                    max=TOTAL_MATCHES,
                                                    className="form-input-custom",
                                                ),
                                            ],
                                            md=3,
                                            className="mb-3",
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Button(
                                                    "Delete Match Data",
                                                    id="admin-delete-btn",
                                                    color="danger",
                                                    className="mt-4",
                                                ),
                                            ],
                                            md=3,
                                            className="mb-3",
                                        ),
                                    ]
                                ),
                                html.Div(id="admin-delete-msg", className="mt-2"),
                            ]
                        ),
                    ],
                    className="admin-card mb-4",
                ),
                # Summary
                html.Div(id="admin-summary", className="mb-4"),
            ],
        ),
    ],
    className="page-content",
)


# ─── Team Management ────────────────────────────────────────────────────────


@callback(
    Output("admin-team-msg", "children"),
    Output("admin-teams-list", "children"),
    Output("admin-team-name", "value"),
    Output("admin-team-abbr", "value"),
    Input("admin-add-team-btn", "n_clicks"),
    Input({"type": "deactivate-team", "index": ALL}, "n_clicks"),
    Input({"type": "reactivate-team", "index": ALL}, "n_clicks"),
    State("admin-team-name", "value"),
    State("admin-team-abbr", "value"),
    State("admin-team-color", "value"),
    prevent_initial_call=True,
)
def manage_teams(add_clicks, deactivate_clicks, reactivate_clicks, name, abbr, color):
    triggered = ctx.triggered_id
    msg = ""

    if triggered == "admin-add-team-btn":
        if not name or not abbr or not color:
            msg = "⚠️ Please fill in all fields"
        else:
            try:
                add_team(name, color, abbr)
                msg = f"✅ Added {name}"
                name, abbr = "", ""
            except Exception as e:
                msg = f"❌ {e}"

    elif isinstance(triggered, dict) and triggered.get("type") == "deactivate-team":
        team_id = triggered["index"]
        deactivate_team(team_id)
        msg = "Team deactivated"

    elif isinstance(triggered, dict) and triggered.get("type") == "reactivate-team":
        team_id = triggered["index"]
        reactivate_team(team_id)
        msg = "Team reactivated"

    # Rebuild teams list
    teams = get_all_teams(active_only=False)
    team_rows = []
    for t in teams:
        status = "Active" if t["active"] else "Inactive"
        btn = (
            dbc.Button(
                "Deactivate",
                id={"type": "deactivate-team", "index": t["id"]},
                color="warning",
                size="sm",
            )
            if t["active"]
            else dbc.Button(
                "Reactivate",
                id={"type": "reactivate-team", "index": t["id"]},
                color="success",
                size="sm",
            )
        )
        team_rows.append(
            html.Div(
                [
                    html.Div(
                        className="lb-color-dot", style={"backgroundColor": t["color"]}
                    ),
                    html.Span(
                        f"{t['name']} ({t['abbreviation']})",
                        className="me-3",
                        style={"color": t["color"] if t["active"] else "#666"},
                    ),
                    html.Span(
                        status,
                        className=f"me-3 {'text-success' if t['active'] else 'text-muted'}",
                    ),
                    btn,
                ],
                className="admin-team-row",
            )
        )

    return msg, html.Div(team_rows), name, abbr


# ─── Generate score fields ──────────────────────────────────────────────────


@callback(
    Output("admin-score-fields", "children"),
    Input("admin-load-match-btn", "n_clicks"),
    Input("admin-add-team-btn", "n_clicks"),  # refresh when team added
    State("admin-match-number", "value"),
    prevent_initial_call=False,
)
def generate_score_fields(load_clicks, _team_add, match_number):
    teams = get_all_teams()
    existing = {}
    if match_number and ctx.triggered_id == "admin-load-match-btn":
        existing = get_match_scores_for_edit(int(match_number))

    fields = []
    for t in teams:
        val = existing.get(t["name"], "")
        fields.append(
            dbc.Col(
                [
                    dbc.Label(
                        t["name"],
                        className="form-label-custom",
                        style={"color": t["color"]},
                    ),
                    dbc.Input(
                        id={"type": "score-input", "index": t["name"]},
                        type="number",
                        step=0.5,
                        placeholder="Points",
                        value=val,
                        className="form-input-custom",
                    ),
                ],
                md=3,
                sm=4,
                xs=6,
                className="mb-3",
            )
        )
    return (
        dbc.Row(fields) if fields else html.P("Add teams first", className="text-muted")
    )


@callback(
    Output("admin-match-team-1", "value"),
    Output("admin-match-team-2", "value"),
    Output("admin-match-stadium", "value"),
    Input("admin-load-match-btn", "n_clicks"),
    State("admin-match-number", "value"),
    prevent_initial_call=True,
)
def load_match_metadata(_n_clicks, match_number):
    if not match_number:
        return "", "", ""

    details = get_match_details(int(match_number))
    return details["team_1"], details["team_2"], details["stadium"]


# ─── Save scores ────────────────────────────────────────────────────────────


@callback(
    Output("admin-scores-msg", "children"),
    Input("admin-save-scores-btn", "n_clicks"),
    State("admin-match-number", "value"),
    State("admin-match-team-1", "value"),
    State("admin-match-team-2", "value"),
    State("admin-match-stadium", "value"),
    State({"type": "score-input", "index": ALL}, "value"),
    State({"type": "score-input", "index": ALL}, "id"),
    prevent_initial_call=True,
)
def save_scores(n_clicks, match_number, team_1, team_2, stadium, values, ids):
    if not match_number:
        return "⚠️ Enter a match number"
    scores = {}
    for v, id_dict in zip(values, ids):
        if v is not None and v != "":
            scores[id_dict["index"]] = float(v)
    if not scores:
        return "⚠️ Enter at least one score"
    upsert_scores(
        int(match_number),
        scores,
        team_1=team_1 or "",
        team_2=team_2 or "",
        stadium=stadium or "",
    )
    return f"✅ Saved scores for Match {match_number}"


# ─── Generate transfer fields ───────────────────────────────────────────────


@callback(
    Output("admin-transfer-fields", "children"),
    Input("admin-load-transfer-btn", "n_clicks"),
    Input("admin-add-team-btn", "n_clicks"),
    State("admin-transfer-match", "value"),
    prevent_initial_call=False,
)
def generate_transfer_fields(load_clicks, _team_add, match_number):
    teams = get_all_teams()
    existing = {}
    if match_number and ctx.triggered_id == "admin-load-transfer-btn":
        existing = get_match_transfers_for_edit(int(match_number))

    fields = []
    for t in teams:
        val = existing.get(t["name"], "")
        fields.append(
            dbc.Col(
                [
                    dbc.Label(
                        t["name"],
                        className="form-label-custom",
                        style={"color": t["color"]},
                    ),
                    dbc.Input(
                        id={"type": "transfer-input", "index": t["name"]},
                        type="number",
                        step=1,
                        min=0,
                        placeholder="Transfers",
                        value=val,
                        className="form-input-custom",
                    ),
                ],
                md=3,
                sm=4,
                xs=6,
                className="mb-3",
            )
        )
    return (
        dbc.Row(fields) if fields else html.P("Add teams first", className="text-muted")
    )


# ─── Save transfers ─────────────────────────────────────────────────────────


@callback(
    Output("admin-transfers-msg", "children"),
    Input("admin-save-transfers-btn", "n_clicks"),
    State("admin-transfer-match", "value"),
    State({"type": "transfer-input", "index": ALL}, "value"),
    State({"type": "transfer-input", "index": ALL}, "id"),
    prevent_initial_call=True,
)
def save_transfers(n_clicks, match_number, values, ids):
    if not match_number:
        return "⚠️ Enter a match number"
    transfers = {}
    for v, id_dict in zip(values, ids):
        if v is not None and v != "":
            transfers[id_dict["index"]] = int(v)
    if not transfers:
        return "⚠️ Enter at least one value"
    upsert_transfers(int(match_number), transfers)
    return f"✅ Saved transfers for Match {match_number}"


# ─── Delete match ────────────────────────────────────────────────────────────


@callback(
    Output("admin-delete-msg", "children"),
    Input("admin-delete-btn", "n_clicks"),
    State("admin-delete-match", "value"),
    prevent_initial_call=True,
)
def delete_match(n_clicks, match_number):
    if not match_number:
        return "⚠️ Enter a match number to delete"
    delete_match_data(int(match_number))
    return f"🗑️ Deleted all data for Match {match_number}"


# ─── Summary ─────────────────────────────────────────────────────────────────


@callback(
    Output("admin-summary", "children"),
    Input("admin-save-scores-btn", "n_clicks"),
    Input("admin-save-transfers-btn", "n_clicks"),
    Input("admin-delete-btn", "n_clicks"),
    Input("admin-add-team-btn", "n_clicks"),
)
def update_summary(*_):
    teams = get_all_teams()
    matches = get_all_matches()
    max_match = get_max_match_number()
    return dbc.Card(
        dbc.CardBody(
            [
                html.H6("📊 Database Summary"),
                html.P(f"Active teams: {len(teams)}"),
                html.P(f"Matches entered: {len(matches)}"),
                html.P(
                    f"Latest match: #{max_match}" if max_match else "No matches yet"
                ),
            ]
        ),
        className="admin-card",
    )
