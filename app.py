import dash
import dash_bootstrap_components as dbc
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
    ]
)


@app.callback(
    Output("output-container", "children"),
    [Input("submit-button", "n_clicks")],
    [State("molecular_formula_input", "value"), State("mdv_a_input", "value")],
)
def update_output(n_clicks, molecular_formula_input, mdv_a_input):
    if n_clicks is not None:
        print(f"You entered: {molecular_formula_input}")
    if molecular_formula_input:
        result = SITA_module.Labelled_compound(
            formula=molecular_formula_input, labelled_element="C", mdv_a=mdv_a_input
        ).mdv_star()
        print(f"Result: {result}")


if __name__ == "__main__":
    app.run_server(debug=True)
