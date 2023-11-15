import logging

import dash
import dash_bootstrap_components as dbc
import numpy as np
from dash import Input, Output, State, dcc, html

import SITA_module

app = dash.Dash(__name__)
app = dash.Dash(external_stylesheets=[dbc.themes.LUX])

app.layout = html.Div(
    [
        html.H1("SITA app"),
        html.P(
            "This app will determine the correction matrix for a given molecular formula eg C8H23NO2Si2 ",
        ),
        html.P(
            "Enter a molecular formula and an MDV ratio eg 0.6228, 0.1517, 0.0749, 0.1507"
        ),
        dcc.Input(
            id="molecular_formula_input",
            type="text",
            placeholder="Enter molecular formula...",
        ),
        dcc.Input(id="mdv_a_input", type="text", placeholder="Enter mdv ratio "),
        dbc.Button("Submit", id="submit-button", color="primary", className="mr-1"),
        html.Div(id="output-container"),
        dcc.Store(id="input-store", storage_type="session"),
        dbc.Button("Download", id="download-button", color="primary"),
        dcc.Download(id="download-matrix"),
    ]
)


@app.callback(
    Output("input-store", "data"),
    [Input("submit-button", "n_clicks")],
    [State("molecular_formula_input", "value"), State("mdv_a_input", "value")],
)
def store_input(n_clicks, molecular_formula_input, mdv_a_input):
    if n_clicks is not None and molecular_formula_input and mdv_a_input:
        result = SITA_module.Labelled_compound(
            formula=molecular_formula_input, labelled_element="C", mdv_a=mdv_a_input
        ).mdv_star()
        return result


@app.callback(
    Output("download-matrix", "data"),
    [Input("download-button", "n_clicks")],
    [State("input-store", "data")],
)
def update_output(ts, stored_data):
    if ts is not None:
        matrix_csv = np.savetxt("mdv_star.csv", stored_data, delimiter=",")
        return matrix_csv


if __name__ == "__main__":
    app.run_server(debug=True)
