import logging
import csv
import dash
from dash import dash_table
import dash_bootstrap_components as dbc
import numpy as np
from dash import Input, Output, State, dcc, html
import pandas as pd

import SITA_module

df = pd.DataFrame()


app = dash.Dash(__name__)
app = dash.Dash(external_stylesheets=[dbc.themes.LUX])

app.layout = html.Div(
    [
        html.H1("SITA app"),
        html.P(
            "This app will determine the correction matrix for a given molecular formula eg C8H23NO2Si2 ",
        ),
        html.P("Enter a molecular formula "),
        dcc.Input(
            id="molecular_formula_input",
            type="text",
            placeholder="Enter molecular formula...",
        ),
        dbc.Button("Submit", id="submit-button", color="primary", className="mr-1"),
        html.Div(id="output-container"),
        dcc.Store(id="input-store", storage_type="session"),
        dbc.Button("Download", id="download-button", color="primary"),
        dcc.Download(id="download-matrix"),
        dcc.Clipboard(id="table_copy", style={"fontSize": 20}),
        dash_table.DataTable(id="table", style_header={"display": "none"}),
    ]
)


@app.callback(
    Output("table", "data"),
    Output("table", "columns"),
    [Input("submit-button", "n_clicks")],
    [State("molecular_formula_input", "value")],
)
def update_table(n_clicks, molecular_formula_input):
    if n_clicks is None:
        return dash.no_update
    if molecular_formula_input:
        result = SITA_module.Labelled_compound(
            formula=molecular_formula_input, labelled_element="C", vector_size=4
        ).correction_matrix()
        df = pd.DataFrame(result)
        data = df.to_dict("records")
        columns = [{"name": "", "id": str(i)} for i in df.columns]
        return data, columns


@app.callback(
    Output("table_copy", "content"),
    Input("table_copy", "n_clicks"),
    State("table", "data"),
)
def copy(_, data):
    dff = pd.DataFrame(data)
    return dff.to_csv(index=False)


if __name__ == "__main__":
    app.run_server(debug=True)
