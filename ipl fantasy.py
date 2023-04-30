#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 23:12:39 2023

@author: ronakpatel
"""

# IMPORTS
from dash import Dash, html, dcc, dash_table, Input, Output
import plotly.express as px
import pandas as pd


# DATA
# read data showing team points per match
match_points_df = pd.read_excel("IPL_Book_2023.xlsx", sheet_name='Match Points')
print(match_points_df)

# contant variables
total_teams = len(match_points_df.columns)
team_names = list(match_points_df.columns[1:])

# leaderboard showing current standings with rank
leaderboard_data = {team_name:sum(match_points_df[team_name]) for team_name in match_points_df.columns[1:]}
leaderboard_df = pd.DataFrame(sorted(leaderboard_data.items(), key=lambda item: item[1], reverse=True), columns=['TEAM','POINTS'])
leaderboard_df['RANK'] = [i for i in range(1,total_teams)]                           
print(leaderboard_df)

# FRONTEND

# initialize app
app = Dash("IPL RASIYA 2023")

    
# app layout and objects
app.layout = html.Div([
        html.H2('RASIYA ANALYTICS', id='page-title'),
        
        # leaderboard panel
        html.Div([
                html.H3('Leaderboard', id='leaderboard-title'),
                dash_table.DataTable(leaderboard_df.to_dict('records'), [{"name": i, "id": i} for i in leaderboard_df.columns], 
                                     style_table={'maxWidth': '20%'},
                                     style_cell_conditional=[
                                        {'if': {'column_id': 'TEAM'},
                                         'width': '30%'},
                                        {'if': {'column_id': 'POINTS'},
                                         'width': '15%'},
                                        {'if': {'column_id': 'RANK'},
                                         'width': '10%'}], id='leaderboard-table')
                ], id='leaderboard-div'),

        # points accumulation by match graph
        html.Div([
                html.H3('Points by Match', id='points_per_match-title'),
                dcc.Dropdown(team_names, team_names[0], id='points_per_match-dropdown'),
                dcc.Graph(id='points_per_match-graph')
                ], id='points_per_match-div')
        
        ])

# callbacks
@app.callback(
    Output('points_per_match-graph', 'figure'),
    Input('points_per_match-dropdown', 'value'))
def update_graph(value):
    x_axis = match_points_df['MATCH_ID']
    y_axis = match_points_df[value]

    fig = px.scatter(match_points_df, x=x_axis, y=y_axis)

    return fig

# main
#if __name__ == "__main__":
#    app.run_server(debug=True)