import pandas as pd
import dash_mantine_components as dmc
import dash_ag_grid as dag
import plotly.express as px

from constants import TEAMS, TEAM_COLORS, DATA_PATH, DATA_TRANSFERS_PATH


def load_data(file_path):
    """Load data from a CSV file and return it as a pandas DataFrame."""
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def create_dag(df):
    """Create a Dash AG Grid component from a pandas DataFrame."""
    if df is None or df.empty:
        print("DataFrame is empty or None.")
        return None

    grid_options = {
        "columnDefs": [{"headerName": col, "field": col} for col in df.columns],
        "rowData": df.to_dict("records"),
        "defaultColDef": {"sortable": True, "filter": True, "resizable": True},
    }

    return dag.AgGrid(
        id="data-grid",
        dashGridOptions=grid_options,
        style={"height": "75vh", "width": "100%"},
        className="ag-theme-alpine",
    )


def create_total_points_chart(df):

    teams = list(df.columns[1:])
    df = df.copy()
    for team in teams:
        df[team] = df[team].cumsum()
    df["Match"] = df.index + 1
    df = df[["Match"] + teams]

    df = df.melt(id_vars="Match", var_name="Team", value_name="Points")
    fig = px.line(
        df, x="Match", y="Points", color="Team", markers=True, line_shape="spline"
    )
    fig.update_traces(mode="lines+markers")
    fig.update_layout(
        height=415,
        plot_bgcolor="white",
        xaxis_title="Match",
        xaxis_range=[df["Match"].min() - 0.5, df["Match"].max() + 0.5],
        yaxis_title="Total Points",
        legend=dict(
            title="", orientation="v", yanchor="top", y=1, xanchor="left", x=1.02
        ),
        margin=dict(l=20, r=20, t=20, b=20),
    )
    return fig


def create_transfers_chart(df):
    df = df.melt(id_vars="Match", var_name="Team", value_name="Transfers")
    fig = px.scatter(
        df,
        x="Match",
        y="Transfers",
        color="Team",
    )
    fig.update_layout(
        height=415,
        plot_bgcolor="white",
        xaxis_title="Match",
        yaxis_title="Transfers",
        legend=dict(
            title="", orientation="v", yanchor="top", y=1, xanchor="left", x=1.02
        ),
        margin=dict(l=20, r=20, t=20, b=20),
        yaxis=dict(tickmode="linear", tick0=0, dtick=1),
    )
    return fig


def create_transfers_accumulated_chart(df):
    df = df.melt(id_vars="Match", var_name="Team", value_name="Transfers")

    df["Transfers accumulated"] = df.groupby("Team")["Transfers"].cumsum()
    df = df.drop(columns=["Transfers"])
    df["Match"] = df["Match"].astype(int)
    df = df.sort_values(by=["Team", "Match"]).reset_index(drop=True)

    fig = px.line(
        df,
        x="Match",
        y="Transfers accumulated",
        color="Team",
        markers=True,
        line_shape="spline",
    )
    fig.update_traces(mode="lines+markers")
    fig.update_layout(
        height=415,
        plot_bgcolor="white",
        xaxis_title="Match",
        yaxis_title="Transfers Accumulated",
        legend=dict(
            title="", orientation="v", yanchor="top", y=1, xanchor="left", x=1.02
        ),
        margin=dict(l=20, r=20, t=20, b=20),
    )
    return fig


def create_transfer_efficiency_chart(df, transfers_df):

    transfers_df.fillna(0, inplace=True)

    df.set_index("Match", inplace=True)
    transfers_df.set_index("Match", inplace=True)

    cumulative_points = df.cumsum()
    cumulative_transfers = transfers_df.cumsum()

    efficiency = cumulative_points / cumulative_transfers.replace(0, pd.NA)

    efficiency = efficiency.reset_index()

    efficiency_melted = efficiency.melt(
        id_vars="Match", var_name="Team", value_name="Transfer Efficiency"
    )
    min_match = efficiency_melted["Match"].min()
    max_match = efficiency_melted["Match"].max()
    fig = px.line(
        efficiency_melted,
        x="Match",
        y="Transfer Efficiency",
        color="Team",
        markers=True,
        line_shape="spline",
    )
    fig.update_traces(mode="lines+markers")
    fig.update_layout(
        height=415,
        plot_bgcolor="white",
        xaxis_title="Match",
        xaxis_range=[
            efficiency_melted["Match"].min() - 0.5,
            efficiency_melted["Match"].max() + 0.5,
        ],
        yaxis_range=[
            efficiency_melted["Transfer Efficiency"][
                efficiency_melted["Match"] == min_match
            ].min()
            - 50,
            efficiency_melted["Transfer Efficiency"][
                efficiency_melted["Match"] == max_match
            ].max()
            + 50,
        ],
        yaxis_title="Efficiency (Points / Transfers)",
        legend=dict(
            title="", orientation="v", yanchor="top", y=1, xanchor="left", x=1.02
        ),
        margin=dict(l=20, r=20, t=20, b=20),
    )

    return fig


def create_points_earned_chart(df):
    df = df.melt(id_vars="Match", var_name="Team", value_name="Points")
    fig = px.scatter(
        df,
        x="Match",
        y="Points",
        color="Team",
        size="Points",
        hover_name="Team",
        size_max=20,
    )
    fig.update_layout(
        height=415,
        plot_bgcolor="white",
        xaxis_title="Match",
        xaxis_range=[df["Match"].min() - 1, df["Match"].max() + 1],
        yaxis_title="Points Earned",
        legend=dict(
            title="", orientation="v", yanchor="top", y=1, xanchor="left", x=1.02
        ),
        margin=dict(l=20, r=20, t=20, b=20),
    )
    return fig


def create_leaderboard_table(df):
    team_points = df.drop(columns=["Match"]).sum().reset_index()
    team_points.columns = ["Team Name", "Total Points"]

    team_points["Rank"] = (
        team_points["Total Points"].rank(ascending=False, method="min").astype(int)
    )

    team_points = team_points.sort_values("Rank")

    table = dag.AgGrid(
        id="rank-table",
        columnDefs=[
            {
                "headerName": "Rank",
                "field": "Rank",
                "maxWidth": 70,
                "minWidth": 40,
                "sortable": True,
            },
            {
                "headerName": "Team Name",
                "field": "Team Name",
                "maxWidth": 160,
                "minWidth": 40,
                "sortable": True,
            },
            {
                "headerName": "Total Points",
                "field": "Total Points",
                "maxWidth": 120,
                "minWidth": 40,
                "sortable": True,
            },
        ],
        rowData=team_points.to_dict("records"),
        className="ag-theme-quartz",
        dashGridOptions={"domLayout": "autoHeight"},
        defaultColDef={
            "autoWidth": True,
            "flex": 1,
        },
    )

    return table


def create_transfers_table(df):
    transfers_df = df.drop(columns=["Match"]).sum().reset_index()
    transfers_df.columns = ["Team Name", "Transfers"]
    transfers_df["Avg"] = (transfers_df["Transfers"] / df["Match"].nunique()).round(2)

    team_points = (
        load_data(
            file_path=DATA_PATH,
        )
        .drop(columns=["Match"])
        .sum()
        .reset_index()
    )
    transfers_df = transfers_df.merge(
        team_points, left_on="Team Name", right_on="index", how="left"
    )
    transfers_df = transfers_df.drop(columns=["index"]).rename(
        columns={"index": "Team Name", 0: "Total Points"}
    )
    transfers_df["Eff"] = (
        transfers_df["Total Points"] / transfers_df["Transfers"]
    ).round(2)

    transfers_df = transfers_df.sort_values("Eff", ascending=False)

    table = dag.AgGrid(
        id="transfers-table",
        columnDefs=[
            {
                "headerName": "Tfrs",
                "field": "Transfers",
                "maxWidth": 60,
                "minWidth": 40,
                "sortable": True,
            },
            {
                "headerName": "Team Name",
                "field": "Team Name",
                "maxWidth": 150,
                "minWidth": 40,
                "sortable": True,
            },
            {
                "headerName": "Avg",
                "field": "Avg",
                "maxWidth": 65,
                "minWidth": 40,
                "sortable": True,
            },
            {
                "headerName": "Eff",
                "field": "Eff",
                "maxWidth": 75,
                "minWidth": 40,
                "sortable": True,
            },
        ],
        rowData=transfers_df.to_dict("records"),
        className="ag-theme-quartz",
        dashGridOptions={"domLayout": "autoHeight"},
        defaultColDef={
            "autoWidth": True,
            "flex": 1,
        },
    )

    return table
