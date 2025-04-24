from dash import Dash, dcc, html, Output, Input, State, no_update
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd

from constants import DATA_PATH, DATA_TRANSFERS_PATH
from helper import (
    load_data,
    create_total_points_chart,
    create_transfers_chart,
    create_transfers_accumulated_chart,
    create_transfer_efficiency_chart,
    create_leaderboard_table,
    create_transfers_table,
    create_points_earned_chart,
)

app = Dash(title="IPL Rasiya 2025", external_stylesheets=dmc.styles.ALL)
server = app.server

app.layout = dmc.MantineProvider(
    [
        dcc.Location(id="app-url", refresh=True),
        dcc.Store(id="store-data"),
        dcc.Store(id="store-transfers-data"),
        html.Div(
            [
                dmc.Grid(
                    [
                        dmc.GridCol(
                            dmc.Image(
                                src="/assets/ipl_rasiya_logo.png",
                            ),
                            span=3,
                        ),
                        dmc.GridCol(
                            [
                                dmc.Text(
                                    "Match",
                                    className="label-styles",
                                ),
                                html.Br(),
                                dmc.RangeSlider(
                                    id="slider-match-range",
                                    min=1,
                                    minRange=5,
                                    size="md",
                                ),
                            ],
                            span=6,
                        ),
                        dmc.GridCol(
                            dmc.MultiSelect(
                                id="drp-team-select",
                                label="Team",
                                labelProps={"className": "label-styles"},
                                placeholder="Select Teams",
                                searchable=True,
                                clearable=True,
                                size="md",
                            ),
                            span=3,
                        ),
                    ],
                    align="center",
                ),
                dmc.Grid(
                    [
                        dmc.GridCol(
                            id="leaderboard-table-div",
                            span=3,
                        ),
                        dmc.GridCol(
                            dcc.Graph(
                                className="chart-styles",
                                id="graph-total-points",
                            ),
                            span=9,
                        ),
                    ],
                ),
                html.Br(),
                dmc.Grid(
                    [
                        dmc.GridCol(
                            id="transfers-table-div",
                            span=3,
                        ),
                        dmc.GridCol(
                            dmc.Tabs(
                                [
                                    dmc.TabsList(
                                        [
                                            dmc.TabsTab(
                                                "Points Earned", value="points-earned"
                                            ),
                                            dmc.TabsTab("Transfers", value="transfers"),
                                            dmc.TabsTab(
                                                "Transfers Accumulated",
                                                value="transfers-accumulated",
                                            ),
                                            dmc.TabsTab(
                                                "Transfer Efficiency",
                                                value="transfer-efficiency",
                                            ),
                                        ]
                                    ),
                                    dmc.TabsPanel(
                                        dcc.Graph(
                                            className="chart-styles",
                                            id="graph-earned-points",
                                        ),
                                        value="points-earned",
                                    ),
                                    dmc.TabsPanel(
                                        dcc.Graph(
                                            className="chart-styles",
                                            id="graph-total-transfers",
                                        ),
                                        value="transfers",
                                    ),
                                    dmc.TabsPanel(
                                        dcc.Graph(
                                            className="chart-styles",
                                            id="graph-transfers-accumulated",
                                        ),
                                        value="transfers-accumulated",
                                    ),
                                    dmc.TabsPanel(
                                        dcc.Graph(
                                            className="chart-styles",
                                            id="graph-transfer-efficiency",
                                        ),
                                        value="transfer-efficiency",
                                    ),
                                ],
                                variant="pills",
                                value="points-earned",
                            ),
                            span=9,
                        ),
                    ],
                ),
            ],
            className="layout-styles",
        ),
    ],
)


@app.callback(
    [
        Output("store-data", "data"),
        Output("store-transfers-data", "data"),
        Output("slider-match-range", "max"),
        Output("slider-match-range", "value"),
        Output("slider-match-range", "marks"),
        Output("drp-team-select", "data"),
        Output("leaderboard-table-div", "children"),
        Output("transfers-table-div", "children"),
    ],
    Input("app-url", "pathname"),
)
def load_data_on_start(pathname):
    if pathname == "/":
        try:
            data_df = load_data(
                file_path=DATA_PATH,
            )
            data_trasfers_df = load_data(
                file_path=DATA_TRANSFERS_PATH,
            )

            max = len(data_df)
            value = [1, len(data_df)]
            marks = [{"value": i for i in range(1, len(data_df) + 1)}]
            team_names = [
                {"value": team, "label": team} for team in data_df.columns[1:]
            ]
            return (
                data_df.to_dict("records"),
                data_trasfers_df.to_dict("records"),
                max,
                value,
                marks,
                team_names,
                create_leaderboard_table(data_df),
                create_transfers_table(data_trasfers_df),
            )
        except FileNotFoundError:
            print("Data file not found. Please ensure the file path is correct.")
            return (
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
    return (
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
    )


@app.callback(
    [
        Output("graph-total-points", "figure"),
        Output("graph-earned-points", "figure"),
        Output("graph-total-transfers", "figure"),
        Output("graph-transfers-accumulated", "figure"),
        Output("graph-transfer-efficiency", "figure"),
    ],
    [
        Input("drp-team-select", "dropdownOpened"),
        Input("drp-team-select", "value"),
        Input("slider-match-range", "value"),
        Input("store-data", "data"),
        Input("store-transfers-data", "data"),
    ],
)
def update_graphs(drpOpen, selected_teams, match_range, data_df, transfers_data_df):

    if drpOpen is True or not data_df:
        return no_update, no_update

    df = pd.DataFrame(data_df)
    transfers_df = pd.DataFrame(transfers_data_df)

    if not selected_teams:
        filtered_df = df.copy()
        filtered_transfers_df = transfers_df.copy()
    else:
        filtered_df = df[["Match"] + selected_teams].copy()
        filtered_transfers_df = transfers_df[["Match"] + selected_teams].copy()
    if filtered_df.empty or filtered_transfers_df.empty:
        return no_update, no_update

    total_points_chart = create_total_points_chart(filtered_df)
    points_earned_chart = create_points_earned_chart(filtered_df)
    transfers_chart = create_transfers_chart(filtered_transfers_df)
    transfers_accumulated_chart = create_transfers_accumulated_chart(
        filtered_transfers_df
    )
    transfer_efficiency_chart = create_transfer_efficiency_chart(
        filtered_df, filtered_transfers_df
    )

    if match_range:
        min_match, max_match = match_range
        total_points_chart.update_layout(xaxis_range=[min_match - 0.5, max_match + 0.5])
        points_earned_chart.update_layout(
            xaxis_range=[min_match - 0.5, max_match + 0.5]
        )
        transfers_chart.update_layout(xaxis_range=[min_match - 0.5, max_match + 0.5])
        transfers_accumulated_chart.update_layout(
            xaxis_range=[min_match - 0.5, max_match + 0.5]
        )
        transfer_efficiency_chart.update_layout(
            xaxis_range=[min_match - 0.5, max_match + 0.5]
        )

    return (
        total_points_chart,
        points_earned_chart,
        transfers_chart,
        transfers_accumulated_chart,
        transfer_efficiency_chart,
    )


if __name__ == "__main__":
    app.run(debug=True, port=8050)
