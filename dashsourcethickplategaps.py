# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 17:20:59 2021
@author: gk3856
source code that generates thick plate gap tool dash
"""
import pyodbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash_table import DataTable

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=10.1.16.100\mes;'
                      'Database=Digitalization;'
                      'Trusted_Connection=yes;')

cursor = conn.cursor()

results = pd.read_sql_query('SELECT * FROM [Digitalization].[HmEng].[vwThickPlateLearning] ORDER BY DischargeTime DESC', conn)

products = pd.read_sql_query('SELECT DISTINCT MillConstantGroup, WidthID, AimFinishThickness, RMGapSetting FROM HmEng.catThickPlateRefGaps_andTolerances', conn)

thickness = products.AimFinishThickness.unique()
thickness = np.sort(thickness)

fig = go.Figure()

dat = products[(products.MillConstantGroup == 1)
                  & (products.WidthID == 4) &
                  (products.AimFinishThickness == 2566)]

dat = dat.to_dict('records')

# Build App
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Thick Plate Gap Tool"),
    html.Label([
        "Select Grade Group:",
        dcc.Dropdown(
            id='grade_radio',
            clearable=False,
            options=[
                {'label': 'Austenitic', 'value': 1},
                {'label': 'Moly', 'value': 2},
                {'label': 'Duplex', 'value': 7},
                {'label': '705', 'value': 10}
            ],
            value=1,
            style={'width': '40%', 'padding': '5px'}
        )
    ]),
    html.Label([
        "Select Width Group:",
        dcc.Dropdown(
            id='width_radio',
            clearable=False,
            options=[
                {'label': '4 Ft (1131-1350mm)', 'value': 3},
                {'label': '5 Ft (1351-1600mm)', 'value': 4}
            ],
            value=4,
            style={'width': '40%', 'padding': '5px'}
        )
    ]),
    html.Label([
        "Select Desired Thickness (mm*100):",
        dcc.Dropdown(
            id='thick-dropdown', 
            clearable=False,
            value=2566, 
            options=[
                {'label': c, 'value': c}
                for c in thickness
            ], 
            style={'width': '40%', 'padding': '5px'})
    ]),
    html.Label([
        "Product Settings:",
        DataTable(
            id='table',
            columns = [{"name": i, "id": i} for i in products.columns],
            data = dat,
            style_header = {'border': '1px solid black'},
            style_cell = {'textAlign': 'left'},
            style_table = {'width': '500px', 'padding': '5px'}
    )]),
    dcc.Graph(
        id='measurements',
        figure = fig)
])

# Define callback to update gap setting
@app.callback(
    Output('table', 'data'),
    [Input('width_radio', 'value'),
    Input('grade_radio', 'value'),
    Input('thick-dropdown', 'value')]
)
def update_table(WidthClass, GradeGroup, Thickness):
    dat = products[(products.MillConstantGroup == GradeGroup)
                  & (products.WidthID == WidthClass) &
                  (products.AimFinishThickness == Thickness)]
    return dat.to_dict('records')

# Define callback to update graph
@app.callback(
    Output('measurements', 'figure'),
    [Input('width_radio', 'value'),
    Input('grade_radio', 'value'),
    Input('thick-dropdown', 'value')]
)
def update_figure(WidthClass, GradeGroup, Thickness):
    df = results[(results.MillConstantGroup == GradeGroup)
                & (results.WidthID == WidthClass) &
                (results.AimFinishThickness == Thickness)]
    df = df[:15]
    fig = go.Figure()
    fig.update_layout(title='White Plate Inspection Measurements and RM Roll Gap vs Time:')
    fig.update_xaxes(title_text='Time')
    fig.update_yaxes(title_text='mm*100')
    fig.add_trace(go.Scatter(x=df["DischargeTime"], y=df["WhiteAvgThickness"], mode='markers', name='WhiteAvgThickness'))
    fig.add_trace(go.Scatter(x=df["DischargeTime"], y=df["UpperThicknessTolerance"], mode='lines', name='Tolerance', marker_color='red'))
    fig.add_trace(go.Scatter(x=df["DischargeTime"], y=df["LowerThicknessTolerance"], mode='lines', name='Tolerance', marker_color='red'))
    fig.add_trace(go.Scatter(x=df["DischargeTime"], y=df["RmRollGap"], mode='markers', name='RMRollGap'))
    return fig

# Run app and display result
app.run_server(host="0.0.0.0", port=8889, debug=True)