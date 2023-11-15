import logging

import dash
from dash import Input, Output, dcc, html


class DashLoggerHandler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)
        self.queue = []

    def emit(self, record):
        msg = self.format(record)
        self.queue.append(msg)


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
dashLoggerHandler = DashLoggerHandler()
logger.addHandler(dashLoggerHandler)

app = dash.Dash()

app.layout = html.Div(
    [
        dcc.Interval(id="interval1", interval=5 * 1000, n_intervals=0),
        html.H1(id="div-out", children="Log"),
        html.Iframe(
            id="console-out", srcDoc="", style={"width": "100%", "height": 400}
        ),
    ]
)


@app.callback(Output("console-out", "srcDoc"), Input("interval1", "n_intervals"))
def update_output(n):
    return "\n".join(dashLoggerHandler.queue)


app.run_server(debug=False, port=8050)
