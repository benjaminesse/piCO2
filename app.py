import os
import pandas as pd
import plotly.express as px
from flask import Flask
from subprocess import call
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input

# Setup the Dash app
server = Flask(__name__)
app = Dash(__name__, server=server, external_stylesheets=[dbc.themes.DARKLY])
app.title = "PiChamber Dashboard"

controls = dbc.Card(
    [

    html.Div(
            [
                dbc.Button(
                    "Shutdown", id="shutdown", color="primary",
                    style={"margin-left": "15px"}
                )
            ]
        )
    ]
)

# =============================================================================
# App Plots
# =============================================================================

plots = dbc.Card(
    [
        html.Div(dcc.Graph(id="co2-chart")),
        html.Div(dcc.Graph(id="temp-chart")),
        html.Div(dcc.Graph(id="humid-chart"))
    ],
    body=True
)

app.layout = dbc.Container(
    [
        html.H1("PiChamber Dashboard"),
        html.Div([dbc.Label("Status")], id="status-text"),
        html.Div([dbc.Label("-")], id="file-text"),
        html.Hr(),
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(controls, md=4),
                        dbc.Col(plots, md=8),
                    ]
                ),
                dcc.Interval(
                    id='interval-component',
                    interval=5000,  # in milliseconds
                    n_intervals=0
                )
            ]
        )
    ],
    fluid=True
)

# =============================================================================
# Callbacks
# =============================================================================

@app.callback(
    [
        Output("co2-chart", "figure"),
        Output("temp-chart", "figure"),
        Output("humid-chart", "figure"),
        Output("status-text", "children"),
        Output("file-text", "children")
    ],
    [
        Input("interval-component", "n_intervals")
    ]
)
def refresh(n_interval):
    """Refresh app plot."""
    # Get the results folder
    res_fnames = os.listdir("Results")
    res_fnames.sort()
    fname = res_fnames[-1]

    # Get the status
    with open('status.txt', 'r') as r:
        status = f'Status: {r.readline().strip()}'

    # Read in the results
    try:
        df = pd.read_csv(f"Results/{fname}", parse_dates=True, skiprows=3)
        df = df.loc[-100:]
    except FileNotFoundError:
        # If the file is not found, return an empty DataFrame
        cols = ["Time", "CO2 (ppm)", "Temperature (C)", "Humidity (%)"]
        df = pd.DataFrame(columns=cols)

    # Generate the time series figure
    co2_fig = px.line(df, x="Time", y="CO2 (ppm)")
    temp_fig = px.line(df, x="Time", y="Temperature (C)")
    humid_fig = px.line(df, x="Time", y="Humidity (%)")
    #time_fig.update_yaxes(range=limits)

    return [co2_fig, temp_fig, humid_fig, status, fname]

@app.callback(
    [],
    [
        Input("shutdown", "n_clicks"),
    ]
)
def shutdown_pi(n):
    call("sudo poweroff", shell=True)

if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0', port=8050)
