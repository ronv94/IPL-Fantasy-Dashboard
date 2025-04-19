import pandas as pd
import dash_mantine_components as dmc
import dash_ag_grid as dag
import plotly.express as px

from constants import TEAMS, TEAM_COLORS


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


def create_line_chart(df):

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


def create_histogram(df):
    df = df.melt(id_vars="Match", var_name="Team", value_name="Points")
    fig = px.bar(
        df,
        x="Match",
        y="Points",
        color="Team",
        barmode="group",
        text_auto=".2s",
    )
    fig.update_layout(
        plot_bgcolor="white",
        xaxis_title="Match",
        yaxis_title="Points Earned",
        legend=dict(
            title="", orientation="v", yanchor="top", y=1, xanchor="left", x=1.02
        ),
    )
    return fig


def create_scatter_plot(df):
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
