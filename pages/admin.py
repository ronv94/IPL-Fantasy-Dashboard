import dash
from datetime import date, datetime

from dash import html, dcc, callback, Input, Output, State, ctx, ALL
import dash_mantine_components as dmc

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
    if not date_value:
        return "Date TBD"

    try:
        parsed_date = datetime.strptime(str(date_value), "%Y-%m-%d")
    except ValueError:
        return str(date_value)

    return parsed_date.strftime("%B %d, %Y")


def _entry_status(score_value, transfer_value):
    has_score = score_value not in (None, "")
    has_transfer = transfer_value not in (None, "")

    if has_score and has_transfer:
        return "Ready", "admin-entry-status-complete"
    if has_score:
        return "Score only", "admin-entry-status-score"
    if has_transfer:
        return "Transfers only", "admin-entry-status-transfer"
    return "Empty", "admin-entry-status-empty"


def _match_number_options():
    matches = get_all_matches()
    if not matches:
        return TOTAL_MATCHES, 1

    today_iso = date.today().isoformat()
    today_matches = sorted(
        m["match_number"] for m in matches if m.get("date_played") == today_iso
    )
    if today_matches:
        default_match = today_matches[0]
    else:
        upcoming_matches = sorted(
            m["match_number"]
            for m in matches
            if m.get("date_played") and m["date_played"] >= today_iso
        )
        default_match = (
            upcoming_matches[0]
            if upcoming_matches
            else get_max_match_number() or matches[0]["match_number"]
        )

    total_pages = max(TOTAL_MATCHES, max(m["match_number"] for m in matches))
    return total_pages, default_match


def _team_logo_src(team_code):
    if not team_code:
        return None
    _, abbreviation = _normalize_ipl_team(team_code)
    normalized_code = abbreviation.strip().lower()
    return dash.get_asset_url(f"images/ipl-teams/{normalized_code}.png")


def _build_fixture_panel(match_number, details):
    team_1_name, team_1_abbr = _normalize_ipl_team(details.get("team_1"))
    team_2_name, team_2_abbr = _normalize_ipl_team(details.get("team_2"))
    stadium = details.get("stadium") or "Stadium TBD"
    match_date = _format_match_date(details.get("date_played"))

    def team_badge(team_name, team_abbr):
        logo_src = _team_logo_src(team_abbr)
        logo = (
            html.Img(src=logo_src, alt=team_name, className="admin-match-team-logo")
            if logo_src
            else html.Div(team_abbr[:3], className="admin-match-team-logo-fallback")
        )
        return html.Div(
            [
                logo,
                html.Span(team_abbr, className="admin-match-team-code"),
            ],
            className="admin-match-team-badge",
        )

    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                f"Match {int(match_number)}",
                                className="admin-match-number-pill",
                            ),
                        ],
                        className="admin-match-meta",
                    ),
                    html.Div(
                        [
                            team_badge(team_1_name, team_1_abbr),
                            html.Span("vs", className="admin-match-versus"),
                            team_badge(team_2_name, team_2_abbr),
                        ],
                        className="admin-match-fixture",
                    ),
                ],
                className="admin-match-fixture-main",
            ),
            html.Div(
                [
                    html.Span("Match Details", className="admin-match-stadium-label"),
                    html.Span(match_date, className="admin-match-detail-date"),
                    html.Span(stadium, className="admin-match-stadium-value"),
                ],
                className="admin-match-stadium",
            ),
        ],
        className="admin-match-fixture-shell",
    )


def _build_match_data_fields(teams, existing_scores, existing_transfers):
    if not teams:
        return dmc.Text("Add teams first", className="text-muted")

    entries = []
    for team in teams:
        team_name = team["name"]
        score_value = existing_scores.get(team_name, "")
        transfer_value = existing_transfers.get(team_name, "")
        status_text, status_class = _entry_status(score_value, transfer_value)
        entries.append(
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        className="lb-color-dot",
                                        style={"backgroundColor": team["color"]},
                                    ),
                                    html.Div(
                                        [
                                            html.Span(
                                                team_name,
                                                className="admin-team-entry-name",
                                                style={"color": team["color"]},
                                            ),
                                            html.Span(
                                                team["abbreviation"],
                                                className="admin-team-entry-abbr",
                                            ),
                                        ],
                                        className="admin-team-entry-labels",
                                    ),
                                ],
                                className="admin-team-entry-heading",
                            ),
                            html.Span(
                                status_text,
                                className=f"admin-entry-status-pill {status_class}",
                            ),
                        ],
                        className="admin-team-entry-team",
                    ),
                    html.Div(
                        [
                            dmc.NumberInput(
                                id={
                                    "type": "match-score-input",
                                    "index": team_name,
                                },
                                step=0.5,
                                placeholder="Enter score",
                                value=score_value,
                                hideControls=True,
                                decimalScale=1,
                                classNames={
                                    "input": "form-input-custom admin-entry-input",
                                },
                            ),
                            dmc.NumberInput(
                                id={
                                    "type": "match-transfer-input",
                                    "index": team_name,
                                },
                                step=1,
                                min=0,
                                placeholder="Enter transfers",
                                value=transfer_value,
                                hideControls=True,
                                allowDecimal=False,
                                classNames={
                                    "input": "form-input-custom admin-entry-input",
                                },
                            ),
                            html.Div(
                                status_text,
                                className=f"admin-entry-status-pill admin-entry-status-mobile {status_class}",
                            ),
                        ],
                        className="admin-team-entry-inputs",
                    ),
                ],
                className="admin-team-entry",
            )
        )

    return html.Div(
        [
            html.Div(
                [
                    html.Div("Team", className="admin-match-grid-head-cell"),
                    html.Div("Score", className="admin-match-grid-head-cell"),
                    html.Div("Transfers", className="admin-match-grid-head-cell"),
                    html.Div("Status", className="admin-match-grid-head-cell"),
                ],
                className="admin-match-grid-head",
            ),
            html.Div(entries, className="admin-match-data-grid"),
        ],
        className="admin-match-entry-shell",
    )


# ─── Layout ──────────────────────────────────────────────────────────────────


def layout():
    pagination_total, default_match = _match_number_options()

    return html.Div(
        [
            html.Div(
                id="admin-panel",
                children=[
                    section_header("Admin Panel", "Manage teams and update match data"),
                    dmc.Paper(
                        [
                            html.Div(
                                html.H5(
                                    "Team Management", className="mb-0 admin-card-title"
                                ),
                                className="admin-card-header",
                            ),
                            html.Div(
                                [
                                    html.Div(
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
                                            html.Div(
                                                [
                                                    html.Label(
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
                                                className="form-field-col mb-3",
                                            ),
                                        ],
                                        className="admin-team-form-grid",
                                    ),
                                    dmc.Button(
                                        "Add Team",
                                        id="admin-add-team-btn",
                                        color="green",
                                        className="admin-action-button",
                                    ),
                                    html.Div(id="admin-team-msg", className="mt-2"),
                                    dmc.Divider(my="md"),
                                    html.H6("Active Teams"),
                                    html.Div(id="admin-teams-list"),
                                ],
                                className="admin-card-body",
                            ),
                        ],
                        className="admin-card mb-4",
                    ),
                    dmc.Paper(
                        [
                            html.Div(
                                html.H5(
                                    "Enter Match Data",
                                    className="mb-0 admin-card-title",
                                ),
                                className="admin-card-header",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        dmc.Pagination(
                                            id="admin-match-pagination",
                                            total=pagination_total,
                                            value=default_match,
                                            withEdges=True,
                                            boundaries=1,
                                            siblings=1,
                                            radius="xl",
                                            size="md",
                                            color="orange",
                                            className="admin-match-pagination",
                                        ),
                                        className="admin-match-pagination-wrap",
                                    ),
                                    html.Div(
                                        id="admin-match-fixture", className="mt-4"
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Div(
                                                        "Entry Progress",
                                                        className="admin-entry-summary-title",
                                                    ),
                                                    html.Div(
                                                        "Existing values load automatically for the selected match. Only filled fields are written when you save.",
                                                        className="admin-entry-summary-note",
                                                    ),
                                                ],
                                                className="admin-entry-summary-copy",
                                            ),
                                            html.Div(
                                                id="admin-match-entry-summary",
                                                className="admin-entry-summary-stats",
                                            ),
                                        ],
                                        className="admin-entry-summary-bar mt-4",
                                    ),
                                    html.Div(id="admin-match-fields", className="mt-4"),
                                    dmc.Button(
                                        "Save Match Data",
                                        id="admin-save-match-data-btn",
                                        color="green",
                                        className="admin-action-button mt-3",
                                    ),
                                    html.Div(
                                        id="admin-match-data-msg", className="mt-2"
                                    ),
                                ],
                                className="admin-card-body",
                            ),
                        ],
                        className="admin-card mb-4",
                    ),
                    dmc.Paper(
                        [
                            html.Div(
                                html.H5(
                                    "⚠️ Danger Zone",
                                    className="mb-0 text-danger admin-card-title",
                                ),
                                className="admin-card-header",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                dmc.NumberInput(
                                                    id="admin-delete-match",
                                                    min=1,
                                                    max=TOTAL_MATCHES,
                                                    value=default_match,
                                                    label="Match # to delete",
                                                    hideControls=True,
                                                    classNames={
                                                        "input": "form-input-custom",
                                                        "label": "form-label-custom",
                                                    },
                                                ),
                                                className="admin-danger-input",
                                            ),
                                            html.Div(
                                                dmc.Button(
                                                    "Delete Match Data",
                                                    id="admin-delete-btn",
                                                    color="red",
                                                    className="admin-danger-button",
                                                ),
                                                className="admin-danger-action",
                                            ),
                                        ],
                                        className="admin-danger-grid",
                                    ),
                                    html.Div(id="admin-delete-msg", className="mt-2"),
                                ],
                                className="admin-card-body",
                            ),
                        ],
                        className="admin-card mb-4",
                    ),
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
            dmc.Button(
                "Deactivate",
                id={"type": "deactivate-team", "index": t["id"]},
                color="yellow",
                size="sm",
                variant="light",
            )
            if t["active"]
            else dmc.Button(
                "Reactivate",
                id={"type": "reactivate-team", "index": t["id"]},
                color="green",
                size="sm",
                variant="light",
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


# ─── Match data editor ─────────────────────────────────────────────────────


@callback(
    Output("admin-match-fixture", "children"),
    Output("admin-match-fields", "children"),
    Output("admin-delete-match", "value"),
    Input("admin-match-pagination", "value"),
    Input("admin-add-team-btn", "n_clicks"),
    Input("admin-delete-btn", "n_clicks"),
    prevent_initial_call=False,
)
def update_match_data_editor(match_number, _team_add, _delete_clicks):
    if not match_number:
        return html.Div(), html.Div(), ""

    match_number = int(match_number)
    teams = get_all_teams()
    details = get_match_details(match_number)
    existing_scores = get_match_scores_for_edit(match_number)
    existing_transfers = get_match_transfers_for_edit(match_number)
    fixture_panel = _build_fixture_panel(match_number, details)
    fields = _build_match_data_fields(teams, existing_scores, existing_transfers)
    return fixture_panel, fields, match_number


@callback(
    Output("admin-match-entry-summary", "children"),
    Input("admin-match-pagination", "value"),
    Input({"type": "match-score-input", "index": ALL}, "value"),
    Input({"type": "match-transfer-input", "index": ALL}, "value"),
)
def update_match_entry_summary(match_number, score_values, transfer_values):
    teams = get_all_teams()
    total_teams = len(teams)
    score_count = sum(value not in (None, "") for value in score_values)
    transfer_count = sum(value not in (None, "") for value in transfer_values)
    completed_rows = sum(
        score not in (None, "") and transfer not in (None, "")
        for score, transfer in zip(score_values, transfer_values)
    )

    summary_items = [
        ("Match", f"#{int(match_number)}" if match_number else "—"),
        ("Teams", str(total_teams)),
        ("Scores", f"{score_count}/{total_teams}" if total_teams else "0/0"),
        (
            "Transfers",
            f"{transfer_count}/{total_teams}" if total_teams else "0/0",
        ),
        (
            "Ready Rows",
            f"{completed_rows}/{total_teams}" if total_teams else "0/0",
        ),
    ]

    return [
        html.Div(
            [
                html.Div(label, className="admin-entry-stat-label"),
                html.Div(value, className="admin-entry-stat-value"),
            ],
            className="admin-entry-stat-card",
        )
        for label, value in summary_items
    ]


# ─── Save match data ───────────────────────────────────────────────────────


@callback(
    Output("admin-match-data-msg", "children"),
    Input("admin-save-match-data-btn", "n_clicks"),
    State("admin-match-pagination", "value"),
    State({"type": "match-score-input", "index": ALL}, "value"),
    State({"type": "match-score-input", "index": ALL}, "id"),
    State({"type": "match-transfer-input", "index": ALL}, "value"),
    State({"type": "match-transfer-input", "index": ALL}, "id"),
    prevent_initial_call=True,
)
def save_match_data(
    n_clicks,
    match_number,
    score_values,
    score_ids,
    transfer_values,
    transfer_ids,
):
    if not match_number:
        return "⚠️ Enter a match number"

    scores = {}
    for v, id_dict in zip(score_values, score_ids):
        if v is not None and v != "":
            scores[id_dict["index"]] = float(v)

    transfers = {}
    for v, id_dict in zip(transfer_values, transfer_ids):
        if v is not None and v != "":
            transfers[id_dict["index"]] = int(v)

    if not scores and not transfers:
        return "⚠️ Enter at least one score or transfer value"

    details = get_match_details(int(match_number))
    if scores:
        upsert_scores(
            int(match_number),
            scores,
            team_1=details.get("team_1", ""),
            team_2=details.get("team_2", ""),
            stadium=details.get("stadium", ""),
            date_played=details.get("date_played", ""),
        )
    if transfers:
        upsert_transfers(int(match_number), transfers)

    saved_parts = []
    if scores:
        saved_parts.append(f"scores for {len(scores)} teams")
    if transfers:
        saved_parts.append(f"transfers for {len(transfers)} teams")
    details_text = " and ".join(saved_parts)
    return f"✅ Saved {details_text} for Match {match_number}"


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
    Input("admin-save-match-data-btn", "n_clicks"),
    Input("admin-delete-btn", "n_clicks"),
    Input("admin-add-team-btn", "n_clicks"),
)
def update_summary(*_):
    teams = get_all_teams()
    matches = get_all_matches()
    max_match = get_max_match_number()
    return dmc.Paper(
        [
            html.H6("📊 Database Summary"),
            html.P(f"Active teams: {len(teams)}"),
            html.P(f"Matches entered: {len(matches)}"),
            html.P(f"Latest match: #{max_match}" if max_match else "No matches yet"),
        ],
        className="admin-card",
        p="lg",
    )
