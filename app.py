import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from dash import Input, Output, State, dash_table, dcc, html

import SITA_module

df = pd.DataFrame()


app = dash.Dash(__name__)
app = dash.Dash(external_stylesheets=[dbc.themes.LUX])

app.layout = html.Div(
    [
        html.H1("SITA app"),
        html.Hr(),
        html.P(
            "This app will determine the correction matrix for a given molecular formula e.g. C8H23NO2Si2 ",
        ),
        html.P("Enter a molecular formula: "),
        dcc.Input(
            id="molecular_formula_input",
            type="text",
            placeholder="Enter molecular formula...",
        ),
        dbc.Button("Submit", id="submit-button", color="primary", className="mr-1"),
        html.Div(id="output-container"),
        html.H4("Copy to Clipboard"),
        dcc.Clipboard(id="table_copy", style={"fontSize": 20}),
        html.H2("Correction matrix", id="matrix_heading", style={"display": "none"}),
        dash_table.DataTable(
            id="table",
            style_header={"display": "none"},
        ),
        html.Footer(
            children=[
                html.Hr(),
                html.P("Created by Cian Monnin"),
                html.A(
                    "At the Metabolomic Innovation Resource, Goodman Cancer Institute, McGill University",
                    href="https://www.mcgill.ca/gci/facilities/metabolomics-innovation-resource-mir",
                ),
                html.Br(),
                html.A("Github", href="https://github.com/CMonnin"),
                html.Hr(),
            ]
        ),
    ],
    style={
        "display": "flex",
        "flexDirection": "column",
        "alignItems": "center",
        "justifyContent": "center",
        "padding": "20px",
    },
)


@app.callback(
    Output("table", "data"),
    Output("table", "columns"),
    Output("matrix_heading", "style"),
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
        print(data)
        columns = [
            {
                "name": "",
                "id": str(i),
            }
            for i in df.columns
        ]
        return data, columns, {"display": "block"}


@app.callback(
    Output("table_copy", "content"),
    Input("table_copy", "n_clicks"),
    State("table", "data"),
)
def copy(_, data):
    df_copy = pd.DataFrame(data)
    return df_copy.to_csv(index=False)


if __name__ == "__main__":
    app.run_server(debug=True)
