import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from dash import Input, Output, State, dash_table, dcc, html

import SITA_module

df = pd.DataFrame()


app = dash.Dash(__name__)
app = dash.Dash(external_stylesheets=[dbc.themes.LUX])
server = app.server
app.layout = html.Div(
    [
        html.H1("SITA app"),
        html.H4("An app to aid in stable isotope tracer experiemnts"),
        html.Hr(style={"width": "60%"}),
        html.P(
            "To determine the correction matrix for a given molecular formula e.g. C8H23NO2Si2 ",
        ),
        html.P("Enter a molecular formula: "),
        dcc.Input(
            id="molecular_formula_input",
            type="text",
            placeholder="Enter molecular formula...",
        ),
        html.P("Enter number of isotopes to calculate: "),
        html.P("Optional. Default is 4 if no value is given. Enter integers only"),
        dcc.Input(
            id="number_of_isotopes",
            type="text",
            placeholder="Number of isotopes...",
        ),
        dbc.Button("Submit", id="submit-button", color="primary", className="mr-1"),
        html.H4("Copy to Clipboard"),
        dcc.Clipboard(id="table_copy", style={"fontSize": 20}),
        html.H2("Correction matrix", id="matrix_heading", style={"display": "none"}),
        dash_table.DataTable(
            id="table",
            style_header={"display": "none"},
        ),
        html.Hr(style={"width": "60%"}),
        html.H4("Correcting via mdv"),
        html.P(
            "If you have the isotope distribution of your analyte of interest and want the corrected distribution: "
        ),
        html.P("Enter a molecular formula: "),
        dcc.Input(
            id="molecular_formula_input_mdv",
            type="text",
            placeholder="Enter molecular formula...",
        ),
        html.P("Enter number of isotopes to calculate: "),
        html.P("Optional. Default is 4 if no value is given. Integers only"),
        dcc.Input(
            id="number_of_isotopes_mdv",
            type="text",
            placeholder="Number of isotopes...",
        ),
        dcc.Input(
            id="user_mdv",
            type="text",
            placeholder="Enter mdv ...",
        ),
        dbc.Button("Submit", id="submit-mdv-button", color="primary", className="mr-1"),
        html.H4("Copy to Clipboard"),
        dcc.Clipboard(id="mdv_star_copy", style={"fontSize": 20}),
        html.H2("mdv_star", id="mdv_star_heading", style={"display": "none"}),
        dash_table.DataTable(
            id="mdv_star_table",
            style_header={"display": "none"},
        ),
        html.H4("Multiple compounds"),
        html.P(
            "Upload a .csv to create an excel workbook for multiple compounds at once"
        ),
        dcc.Upload(
            id="upload-data",
            children=html.Div(["Drag and Drop or ", html.A("Select a file")]),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            # Don't allow multiple files to be uploaded
            multiple=False,
        ),
        html.Div(id="output-data-upload"),
        # Footer
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
    [State("number_of_isotopes", "value")],
)
def update_table(n_clicks, molecular_formula_input, number_of_isotopes):
    if not number_of_isotopes:
        number_of_isotopes = 4
    else:
        number_of_isotopes = int(number_of_isotopes)
    if n_clicks is None:
        return dash.no_update
    if molecular_formula_input:
        result = SITA_module.LabelledCompound(
            formula=molecular_formula_input,
            labelled_element="C",
            vector_size=number_of_isotopes,
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
def copy_table(_, data):
    df_copy = pd.DataFrame(data)
    return df_copy.to_csv(index=False)


# callback for mdv
@app.callback(
    Output("mdv_star_table", "data"),
    Output("mdv_star_table", "columns"),
    Output("mdv_star_heading", "style"),
    [Input("submit-mdv-button", "n_clicks")],
    [State("molecular_formula_input_mdv", "value")],
    [State("number_of_isotopes_mdv", "value")],
    [State("user_mdv", "value")],
)
def update_table_mdv(n_clicks, molecular_formula_input, number_of_isotopes, user_mdv):
    if not number_of_isotopes:
        number_of_isotopes = 4
    else:
        number_of_isotopes = int(number_of_isotopes)
    if n_clicks is None:
        return dash.no_update
    if molecular_formula_input:
        result = SITA_module.LabelledCompound(
            formula=molecular_formula_input,
            labelled_element="C",
            vector_size=number_of_isotopes,
            mdv_a=user_mdv,
        ).mdv_star()
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
    Output("mdv_star_copy", "content"),
    Input("mdv_star_copy", "n_clicks"),
    State("mdv_star_table", "data"),
)
def copy(_, data):
    df_copy = pd.DataFrame(data)
    return df_copy.to_csv(index=False)


if __name__ == "__main__":
    app.run_server(debug=True)
