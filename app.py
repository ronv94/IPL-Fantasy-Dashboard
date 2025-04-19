from dash import Dash, dcc, html, Output, Input, State, no_update
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

from helper import (
    load_data,
    create_line_chart,
    create_histogram,
    create_leaderboard_table,
    create_scatter_plot,
)

app = Dash(title="IPL Rasiya 2025", external_stylesheets=dmc.styles.ALL)

data_df = load_data(file_path="./data/IPLRasiyaData2025.csv")
print(data_df)

app.layout = dmc.MantineProvider(
    html.Div(
        [
            dmc.Grid(
                [
                    dmc.GridCol(
                        dmc.Title("IPL Rasiya 2025", order=1, className="title-styles"),
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
                                max=len(data_df),
                                value=[1, len(data_df)],
                                minRange=5,
                                marks=[
                                    {"value": i for i in range(1, len(data_df) + 1)}
                                ],
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
                            data=[
                                {"value": team, "label": team}
                                for team in data_df.columns[1:]
                            ],
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
                        create_leaderboard_table(data_df),
                        span=3,
                    ),
                    dmc.GridCol(
                        dcc.Graph(
                            figure=create_line_chart(data_df),
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
                            figure=create_scatter_plot(data_df),
                            className="chart-styles",
                            id="graph-earned-points",
                        ),
                        span=9,
                    ),
                ],
            ),
        ],
        className="layout-styles",
    ),
)


@app.callback(
    [Output("graph-total-points", "figure"), Output("graph-earned-points", "figure")],
    [
        Input("drp-team-select", "dropdownOpened"),
        Input("drp-team-select", "value"),
        Input("slider-match-range", "value"),
    ],
)
def update_graphs(drpOpen, selected_teams, match_range):
    if drpOpen is True:
        return no_update, no_update

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
