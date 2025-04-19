from dash import Dash, dcc, html, Output, Input, State, no_update
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd

from helper import (
    load_data,
    create_line_chart,
    create_histogram,
    create_leaderboard_table,
    create_scatter_plot,
)

app = Dash(title="IPL Rasiya 2025", external_stylesheets=dmc.styles.ALL)
server = app.server

app.layout = dmc.MantineProvider(
    [
        dcc.Location(id="app-url", refresh=True),
        dcc.Store(id="store-data"),
        html.Div(
            [
                dmc.Grid(
                    [
                        dmc.GridCol(
                            dmc.Title(
                                "IPL Rasiya 2025", order=1, className="title-styles"
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
                ),
                html.Br(),
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
                            span=3,
                        ),
                        dmc.GridCol(
                            dcc.Graph(
                                className="chart-styles",
                                id="graph-earned-points",
                            ),
                            id="graph-earned-points-div",
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
        Output("slider-match-range", "max"),
        Output("slider-match-range", "value"),
        Output("slider-match-range", "marks"),
        Output("drp-team-select", "data"),
        Output("leaderboard-table-div", "children"),
    ],
    Input("app-url", "pathname"),
)
def load_data_on_start(pathname):
    if pathname == "/":
        try:
            data_df = load_data(file_path="./data/IPLRasiyaData2025.csv")
            max = len(data_df)
            value = [1, len(data_df)]
            marks = [{"value": i for i in range(1, len(data_df) + 1)}]
            team_names = [
                {"value": team, "label": team} for team in data_df.columns[1:]
            ]
            return (
                data_df.to_dict("records"),
                max,
                value,
                marks,
                team_names,
                create_leaderboard_table(data_df),
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
            )
    return (
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
    )


@app.callback(
    [Output("graph-total-points", "figure"), Output("graph-earned-points", "figure")],
    [
        Input("drp-team-select", "dropdownOpened"),
        Input("drp-team-select", "value"),
        Input("slider-match-range", "value"),
        Input("store-data", "data"),
    ],
)
def update_graphs(drpOpen, selected_teams, match_range, data_df):

    if drpOpen is True:
        return no_update, no_update

    data_df = pd.DataFrame(data_df)
    if not selected_teams:
        filtered_df = data_df.copy()
    else:
        filtered_df = data_df[["Match"] + selected_teams].copy()

    if match_range:
        min_match, max_match = match_range
        filtered_df = filtered_df[
            (filtered_df["Match"] >= min_match) & (filtered_df["Match"] <= max_match)
        ]

    if filtered_df.empty:
        return no_update, no_update

    line_chart = create_line_chart(filtered_df)
    scatter_plot = create_scatter_plot(filtered_df)

    return line_chart, scatter_plot


if __name__ == "__main__":
    app.run(debug=True, port=8050)
