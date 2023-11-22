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
        dcc.Clipboard(id="table_copy", style={"fontSize": 20}),
        dash_table.DataTable(
            id="table",
            style_header={"display": "none"},
        ),
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
        print(data)
        columns = [
            {
                "name": "",
                "id": str(i),
            }
            for i in df.columns
        ]
        return data, columns


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
