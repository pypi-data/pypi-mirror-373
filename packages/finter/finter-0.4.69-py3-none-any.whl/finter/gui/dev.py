class FinterGUI:
    @staticmethod
    def run():
        from jupyter_dash import JupyterDash

        JupyterDash.infer_jupyter_proxy_config()

        import base64
        import importlib.util
        import io
        import logging
        import sys

        import dash
        import dash_ace
        import matplotlib.pyplot as plt
        from dash import Input, Output, State, dcc, html

        from finter import Simulation

        logging.basicConfig(filename="/tmp/app.log", filemode="w", level=logging.DEBUG)

        app = JupyterDash(__name__)

        app.layout = html.Div(
            children=[
                html.H1(
                    children="Dash Simulation Example",
                    style={"textAlign": "center", "color": "#4CAF50"},
                ),
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.Label("Universe"),
                                dcc.Dropdown(
                                    id="universe-dropdown",
                                    options=[
                                        {"label": "KR Stock", "value": "kr_stock"},
                                        {"label": "US Stock", "value": "us_stock"},
                                    ],
                                    value="kr_stock",
                                ),
                            ],
                            style={
                                "display": "inline-block",
                                "width": "30%",
                                "paddingRight": "10px",
                            },
                        ),
                        html.Div(
                            children=[
                                html.Label("Model Type"),
                                dcc.Dropdown(
                                    id="model-dropdown",
                                    options=[
                                        {"label": "Alpha", "value": "alpha"},
                                        {"label": "Portfolio", "value": "portfolio"},
                                    ],
                                    value="alpha",
                                ),
                            ],
                            style={
                                "display": "inline-block",
                                "width": "30%",
                                "paddingRight": "10px",
                            },
                        ),
                    ],
                    style={"display": "flex"},
                ),
                html.Br(),
                html.Div(
                    children=[
                        html.Label("Date Range"),
                        dcc.DatePickerRange(
                            id="date-picker-range",
                            start_date="2023-01-01",
                            end_date="2023-12-31",
                        ),
                    ],
                    style={"display": "inline-block", "width": "30%"},
                ),
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                dash_ace.DashAceEditor(
                                    id="code-editor",
                                    value="""from finter import BaseAlpha\nfrom datetime import datetime, timedelta\n\n\nclass Alpha(BaseAlpha):\n    def get(self, start, end):\n        lookback_days = 365\n        pre_start = datetime.strptime(str(start), "%Y%m%d") - timedelta(days=lookback_days)\n        pre_start = int(pre_start.strftime("%Y%m%d"))\n        close = self.get_cm("content.fnguide.ftp.price_volume.price_close.1d").get_df(pre_start, end)\n        close = close.loc[str(pre_start):str(end)]\n        momentum_21d = close.pct_change(21)\n        stock_rank = momentum_21d.rank(pct=True, axis=1)\n        stock_top10 = stock_rank[stock_rank >= 0.9]\n        stock_top10_rolling = stock_top10.rolling(21).apply(lambda x: x.mean())\n        stock_ratio = stock_top10_rolling.div(stock_top10_rolling.sum(axis=1), axis=0)\n        position = stock_ratio * 1e8\n        alpha = position.shift(1)\n        return alpha.loc[str(start):str(end)]""",
                                    theme="monokai",
                                    mode="python",
                                    tabSize=4,
                                    enableBasicAutocompletion=True,
                                    enableLiveAutocompletion=True,
                                    style={
                                        "height": "400px",
                                        "width": "100%",
                                        "border": "1px solid #ccc",
                                        "borderRadius": "4px",
                                        "marginBottom": "10px",
                                    },
                                ),
                                html.Button(
                                    "Simulate",
                                    id="simulate-button",
                                    n_clicks=0,
                                    style={
                                        "width": "48%",
                                        "padding": "10px",
                                        "backgroundColor": "#4CAF50",
                                        "color": "white",
                                        "border": "none",
                                        "borderRadius": "4px",
                                        "cursor": "pointer",
                                        "display": "inline-block",
                                    },
                                ),
                                html.Button(
                                    "Submit",
                                    id="submit-button",
                                    n_clicks=0,
                                    style={
                                        "width": "48%",
                                        "padding": "10px",
                                        "backgroundColor": "#008CBA",
                                        "color": "white",
                                        "border": "none",
                                        "borderRadius": "4px",
                                        "cursor": "pointer",
                                        "display": "inline-block",
                                        "marginLeft": "2%",
                                    },
                                ),
                            ],
                            style={
                                "display": "inline-block",
                                "verticalAlign": "top",
                                "width": "70%",
                                "paddingRight": "20px",
                                "boxSizing": "border-box",
                            },
                        ),
                        html.Div(
                            id="plot-div",
                            style={
                                "display": "inline-block",
                                "width": "25%",
                                "verticalAlign": "top",
                                "border": "1px solid #ccc",
                                "borderRadius": "4px",
                                "padding": "10px",
                                "boxSizing": "border-box",
                                "backgroundColor": "#f9f9f9",
                                "minHeight": "400px",
                            },
                        ),
                    ],
                    style={"display": "flex", "justifyContent": "center"},
                ),
                dcc.Loading(
                    id="loading-1",
                    type="default",
                    children=html.Div(id="loading-output"),
                ),
                html.Div(
                    id="output-div",
                    children="Output will be shown here",
                    style={
                        "width": "70%",
                        "border": "1px solid #ccc",
                        "borderRadius": "4px",
                        "padding": "10px",
                        "boxSizing": "border-box",
                        "backgroundColor": "#f9f9f9",
                        "marginTop": "20px",
                        "whiteSpace": "pre-wrap",
                        "wordBreak": "break-word",
                    },
                ),
                dcc.Store(id="simulation-result"),
            ],
            style={
                "fontFamily": "Arial, sans-serif",
                "margin": "0",
                "padding": "0",
                "boxSizing": "border-box",
            },
        )

        @app.callback(
            [Output("simulation-result", "data"), Output("loading-output", "children")],
            [Input("simulate-button", "n_clicks")],
            [
                State("universe-dropdown", "value"),
                State("model-dropdown", "value"),
                State("date-picker-range", "start_date"),
                State("date-picker-range", "end_date"),
                State("code-editor", "value"),
            ],
        )
        def start_simulation(n_clicks, universe, model, start_date, end_date, code):
            if n_clicks > 0:
                try:
                    # Save the code to a temporary file
                    temp_file_path = "/tmp/temp_alpha.py"
                    with open(temp_file_path, "w") as temp_file:
                        temp_file.write(code)

                    # Import the module from the temporary file
                    spec = importlib.util.spec_from_file_location(
                        "temp_alpha", temp_file_path
                    )
                    temp_alpha = importlib.util.module_from_spec(spec)
                    sys.modules["temp_alpha"] = temp_alpha
                    spec.loader.exec_module(temp_alpha)

                    alpha_instance = temp_alpha.Alpha()

                    # Redirect stdout to capture print statements
                    old_stdout = sys.stdout
                    sys.stdout = buffer = io.StringIO()

                    position = alpha_instance.get(
                        int(start_date.replace("-", "")), int(end_date.replace("-", ""))
                    )

                    # Reset stdout
                    sys.stdout = old_stdout

                    # Get the print output
                    print_output = buffer.getvalue()

                    # Run the simulation
                    simulation = Simulation(universe, model, position, benchmark=None)
                    result = simulation.run(
                        int(start_date.replace("-", "")), int(end_date.replace("-", ""))
                    )

                    # Debug output for position and inputs
                    output = (
                        f"Universe: {universe}\n"
                        f"Model: {model}\n"
                        f"Start Date: {start_date}\n"
                        f"End Date: {end_date}\n"
                        f"Simulation Result:\n{result.cummulative_return.head()}\n"
                        f"Print Output:\n{print_output}\n"
                    )

                    # Capture the plot
                    fig, ax = plt.subplots()
                    result.cummulative_return.plot(ax=ax)
                    buf = io.BytesIO()
                    plt.savefig(buf, format="png")
                    plt.close(fig)
                    buf.seek(0)
                    image_base64 = base64.b64encode(buf.read()).decode("utf-8")
                    plot_div_content = f"data:image/png;base64,{image_base64}"

                    return {
                        "output": output,
                        "plot": plot_div_content,
                    }, "Simulation completed."
                except Exception as e:
                    return {
                        "output": str(e),
                        "plot": "",
                    }, "Error occurred during simulation."
            return dash.no_update, dash.no_update

        @app.callback(
            [Output("output-div", "children"), Output("plot-div", "children")],
            [Input("simulation-result", "data"), Input("submit-button", "n_clicks")],
        )
        def display_result(data, submit_n_clicks):
            ctx = dash.callback_context
            if not ctx.triggered:
                return "Output will be shown here", "Plot will be shown here"

            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

            if trigger_id == "submit-button":
                return "테스트", "Plot will be shown here"

            if trigger_id == "simulation-result" and data:
                output = html.Pre(data["output"])
                plot = (
                    html.Img(
                        src=data["plot"], style={"maxWidth": "100%", "height": "auto"}
                    )
                    if data["plot"]
                    else "Plot will be shown here"
                )
                return output, plot

            return "Output will be shown here", "Plot will be shown here"

        app.run_server(mode="jupyterlab", port=8050)
