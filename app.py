import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, State, dash_table, dcc, html

import SITA_module

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server


def labelled_input(label, input_component, help_text=None):
    children = [dbc.Label(label, html_for=input_component.id)]
    if help_text:
        children.append(html.Small(help_text, className="text-muted d-block mb-1"))
    children.append(input_component)
    return html.Div(children, className="mb-3")


def result_card(title, table_id, copy_id, heading_id):
    return html.Div(
        id=heading_id,
        style={"display": "none"},
        children=dbc.Card(
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.H5(title, className="mb-0 me-2"),
                            dcc.Clipboard(
                                id=copy_id, style={"fontSize": 18}, title="Copy CSV to clipboard"
                            ),
                        ],
                        className="d-flex align-items-center mb-3",
                    ),
                    dash_table.DataTable(
                        id=table_id,
                        style_header={"display": "none"},
                        style_cell={
                            "textAlign": "right",
                            "padding": "6px 12px",
                            "fontFamily": "monospace",
                        },
                        style_table={"overflowX": "auto"},
                    ),
                ]
            ),
            className="mt-3",
        ),
    )


matrix_section = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Correction matrix", className="card-title"),
            html.P(
                "Generate the natural-abundance correction matrix for a given "
                "fragment. Example: alanine (M-57)+ is C11H26NO2Si2 with 3 backbone "
                "carbons.",
                className="text-muted",
            ),
            labelled_input(
                "Molecular formula",
                dbc.Input(
                    id="molecular_formula_input",
                    type="text",
                    placeholder="e.g. C11H26NO2Si2",
                ),
            ),
            labelled_input(
                "Backbone carbons",
                dbc.Input(
                    id="backbone_c", type="number", min=0, placeholder="e.g. 3"
                ),
                help_text=(
                    "Number of C atoms subject to 13C labelling (not total C in the "
                    "fragment). Matrix size is derived as backbone_c + 1."
                ),
            ),
            html.Div(id="matrix_error", className="text-danger small mb-2"),
            dbc.Button("Compute matrix", id="submit-button", color="primary"),
            dcc.Loading(
                result_card(
                    "Correction matrix",
                    table_id="table",
                    copy_id="table_copy",
                    heading_id="matrix_heading",
                ),
                type="default",
            ),
        ]
    )
)


mdv_section = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Corrected MDV (MDV*)", className="card-title"),
            html.P(
                "Apply the correction matrix to a measured mass distribution "
                "vector. Output is normalised to sum to 1.",
                className="text-muted",
            ),
            dbc.Alert(
                [
                    html.Strong("Note: "),
                    "this returns MDV* (natural-abundance-corrected) only. It does "
                    "not apply the unlabelled-biomass correction (Nanchen 2007 "
                    "Eq. 5). For that, call ",
                    html.Code("LabelledCompound.mdv_AA()"),
                    " programmatically.",
                ],
                color="info",
                className="small py-2",
            ),
            labelled_input(
                "Molecular formula",
                dbc.Input(
                    id="molecular_formula_input_mdv",
                    type="text",
                    placeholder="e.g. C11H26NO2Si2",
                ),
            ),
            labelled_input(
                "Backbone carbons",
                dbc.Input(
                    id="backbone_c_mdv", type="number", min=0, placeholder="e.g. 3"
                ),
            ),
            labelled_input(
                "Measured MDV",
                dbc.Input(
                    id="user_mdv",
                    type="text",
                    placeholder="e.g. 0.6228, 0.1517, 0.0749, 0.1507",
                ),
                help_text="Comma-separated values summing to ~1. Length must equal backbone_c + 1.",
            ),
            html.Div(id="mdv_error", className="text-danger small mb-2"),
            dbc.Button("Compute MDV*", id="submit-mdv-button", color="primary"),
            dcc.Loading(
                result_card(
                    "MDV*",
                    table_id="mdv_star_table",
                    copy_id="mdv_star_copy",
                    heading_id="mdv_star_heading",
                ),
                type="default",
            ),
        ]
    ),
    className="mt-4",
)


references_section = dbc.Card(
    dbc.CardBody(
        [
            html.H4("References", className="card-title"),
            html.P(
                "The natural-abundance correction math follows:",
                className="text-muted small mb-2",
            ),
            html.Ul(
                [
                    html.Li(
                        [
                            "Nanchen, A., Fuhrer, T., Sauer, U. (2007). ",
                            html.Em(
                                "Determination of Metabolic Flux Ratios From "
                                "13C-Experiments and Gas Chromatography-Mass "
                                "Spectrometry Data: Protocol and Principles."
                            ),
                            " In: Metabolomics (Methods in Molecular Biology 358), "
                            "Humana Press, pp. 177-197. doi:",
                            html.A(
                                "10.1007/978-1-59745-244-1_11",
                                href="https://doi.org/10.1007/978-1-59745-244-1_11",
                            ),
                            ".",
                        ],
                        className="small",
                    ),
                    html.Li(
                        [
                            "Fischer, E., Zamboni, N., Sauer, U. (2004). ",
                            html.Em(
                                "High-throughput metabolic flux analysis based "
                                "on gas chromatography-mass spectrometry derived "
                                "13C constraints."
                            ),
                            " Analytical Biochemistry 325(2):308-316. doi:",
                            html.A(
                                "10.1016/j.ab.2003.10.036",
                                href="https://doi.org/10.1016/j.ab.2003.10.036",
                            ),
                            ".",
                        ],
                        className="small",
                    ),
                ],
                className="mb-0",
            ),
        ]
    ),
    className="mt-4",
)


footer = html.Footer(
    [
        html.Hr(),
        html.P(
            [
                "Created by Cian Monnin at the ",
                html.A(
                    "Metabolomic Innovation Resource, Goodman Cancer Institute, McGill University",
                    href="https://www.mcgill.ca/gci/facilities/metabolomics-innovation-resource-mir",
                ),
                ". Source on ",
                html.A("GitHub", href="https://github.com/CMonnin"),
                ".",
            ],
            className="text-center text-muted small",
        ),
    ],
    className="mt-5",
)


app.layout = dbc.Container(
    [
        html.Div(
            [
                html.H1("SITA", className="display-5"),
                html.P(
                    "Natural-abundance correction for GC-MS mass distribution "
                    "vectors from 13C stable-isotope tracer experiments.",
                    className="lead",
                ),
            ],
            className="my-4",
        ),
        matrix_section,
        mdv_section,
        references_section,
        footer,
    ],
    style={"maxWidth": "900px"},
    className="py-3",
)


@app.callback(
    Output("table", "data"),
    Output("table", "columns"),
    Output("matrix_heading", "style"),
    Output("matrix_error", "children"),
    Input("submit-button", "n_clicks"),
    State("molecular_formula_input", "value"),
    State("backbone_c", "value"),
    prevent_initial_call=True,
)
def update_table(n_clicks, formula, backbone_c):
    if not formula or backbone_c is None:
        return [], [], {"display": "none"}, "Formula and backbone carbons are required."
    try:
        result = SITA_module.LabelledCompound(
            formula=formula, labelled_element="C", backbone_c=int(backbone_c)
        ).correction_matrix()
    except (ValueError, KeyError) as exc:
        return [], [], {"display": "none"}, str(exc)
    df = pd.DataFrame(result)
    data = df.to_dict("records")
    columns = [{"name": str(i), "id": str(i)} for i in df.columns]
    return data, columns, {"display": "block"}, ""


@app.callback(
    Output("table_copy", "content"),
    Input("table_copy", "n_clicks"),
    State("table", "data"),
    prevent_initial_call=True,
)
def copy_table(_, data):
    return pd.DataFrame(data).to_csv(index=False)


@app.callback(
    Output("mdv_star_table", "data"),
    Output("mdv_star_table", "columns"),
    Output("mdv_star_heading", "style"),
    Output("mdv_error", "children"),
    Input("submit-mdv-button", "n_clicks"),
    State("molecular_formula_input_mdv", "value"),
    State("backbone_c_mdv", "value"),
    State("user_mdv", "value"),
    prevent_initial_call=True,
)
def update_table_mdv(n_clicks, formula, backbone_c, user_mdv):
    if not formula or backbone_c is None or not user_mdv:
        return [], [], {"display": "none"}, "Formula, backbone carbons, and MDV are required."
    try:
        result = SITA_module.LabelledCompound(
            formula=formula,
            labelled_element="C",
            backbone_c=int(backbone_c),
            mdv_a=user_mdv,
        ).mdv_star()
    except (ValueError, KeyError) as exc:
        return [], [], {"display": "none"}, str(exc)
    df = pd.DataFrame(result)
    data = df.to_dict("records")
    columns = [{"name": str(i), "id": str(i)} for i in df.columns]
    return data, columns, {"display": "block"}, ""


@app.callback(
    Output("mdv_star_copy", "content"),
    Input("mdv_star_copy", "n_clicks"),
    State("mdv_star_table", "data"),
    prevent_initial_call=True,
)
def copy_mdv(_, data):
    return pd.DataFrame(data).to_csv(index=False)


if __name__ == "__main__":
    app.run(debug=True)
