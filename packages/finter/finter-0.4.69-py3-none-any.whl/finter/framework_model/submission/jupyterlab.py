import os
import threading
import time
from typing import Any, Tuple

from IPython.display import HTML, display
from ipywidgets import IntText, widgets
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

from finter.framework_model.submission.config import get_model_info
from finter.framework_model.submission.helper_notebook import NotebookExtractor
from finter.framework_model.submission.helper_path import FileManager
from finter.framework_model.submission.helper_poetry import prepare_docker_submit_files
from finter.framework_model.submission.helper_position import load_model_instance
from finter.framework_model.submission.helper_submission import submit_model
from finter.framework_model.submission.helper_ui import MAC_STYLE
from finter.framework_model.submission.notebook import name_exist
from finter.framework_model.validation import ValidationHelper

AVAILABLE_MARKETS = [
    "kr_stock",
    "us_stock",
    "us_etf",
    "us_future",
    "id_stock",
    "id_bond",
    "id_fund",
    "vn_stock",
    "btcusdt_spot_binance",
]
IMAGE_OPTIONS = [
    "sagemaker-distribution:2.1.0-gpu",
]

MACHINE_OPTIONS = ["g4dn.2xlarge"]


class JupyterLabSubmission(NotebookExtractor):
    def __init__(
        self,
        start_date: int = 20150101,
        end_date: int = 20231231,
        model_name: str = "",
        model_universe: str = "kr_stock",
        gpu: bool = False,
    ):
        super().__init__()

        self.start_date = start_date
        self.end_date = end_date
        self.default_modelname = model_name
        self.default_model_universe = model_universe
        self.default_gpu = gpu
        self.default_image = IMAGE_OPTIONS[0]
        self.default_machine = MACHINE_OPTIONS[0]

        self.setup_ui()
        self.register_event_handlers()
        self.update_info_display()

    def setup_ui(self):
        self.setup_sidecar()
        self.create_widgets()
        self.setup_layout()

    def setup_sidecar(self):
        from sidecar import Sidecar

        self.sidecar = Sidecar(title="Submission Dashboard")

    def on_gpu_checkbox_change(self, change):
        if change["new"]:
            self.image_dropdown.layout.display = "block"
            self.machine_dropdown.layout.display = "block"
        else:
            self.image_dropdown.layout.display = "none"
            self.machine_dropdown.layout.display = "none"

    def create_widgets(self):
        self.model_name_input, self.model_universe_dropdown = (
            self.create_input_widgets()
        )

        self.gpu_checkbox = widgets.Checkbox(
            value=self.default_gpu,
            description="GPU Submission",
            disabled=False,
            indent=False,
        )

        self.image_dropdown = widgets.Dropdown(
            options=IMAGE_OPTIONS,
            value=self.default_image,
            description="Image",
            layout=widgets.Layout(width="auto", display="none"),
        )

        self.machine_dropdown = widgets.Dropdown(
            options=MACHINE_OPTIONS,
            value=self.default_machine,
            description="Machine",
            layout=widgets.Layout(width="auto", display="none"),
        )

        self.gpu_checkbox.observe(self.on_gpu_checkbox_change, names="value")

        self.title = self.create_title_widget()
        self.code_display = self.create_code_display_widget()

        self.status_output = widgets.Output()
        (
            self.submit_button,
            self.cancel_button,
            self.position_button,
            self.simulation_button,
            self.refresh_button,
            self.progress,
        ) = self.create_action_widgets()

        self.start_date_input = IntText(
            value=self.start_date,
            description="Start",
            style={"description_width": "initial"},
            layout=widgets.Layout(width="auto"),
        )
        self.end_date_input = IntText(
            value=self.end_date,
            description="End",
            style={"description_width": "initial"},
            layout=widgets.Layout(width="auto"),
        )

    def setup_layout(self):
        layout = widgets.VBox(
            [
                self.title,
                widgets.HBox(
                    [self.start_date_input, self.end_date_input],
                    layout=widgets.Layout(margin="10px 0"),
                ),
                widgets.HBox(
                    [self.model_name_input, self.model_universe_dropdown],
                    layout=widgets.Layout(margin="0"),
                ),
                widgets.HBox(
                    [self.gpu_checkbox, self.image_dropdown, self.machine_dropdown],
                    layout=widgets.Layout(margin="0"),
                ),
                self.create_action_layout(),
                self.status_output,
                self.code_display,
            ],
            layout=widgets.Layout(padding="20px"),
        )
        self.sidecar.clear_output()
        with self.sidecar:
            display(layout)

    def register_event_handlers(self):
        self.model_name_input.observe(self.on_modelname_change, names="value")
        self.model_universe_dropdown.observe(self.on_modelname_change, names="value")
        self.submit_button.on_click(self.on_submit)
        self.cancel_button.on_click(self.on_cancel)
        self.refresh_button.on_click(self.on_refresh)
        self.position_button.on_click(self.on_position_click)
        self.simulation_button.on_click(self.on_simulation_click)

    def create_title_widget(self) -> widgets.HTML:
        return widgets.HTML(
            value="<h1 style='text-align:center;'>Submission Dashboard</h1>"
        )

    def create_code_display_widget(self) -> widgets.HTML:
        code_display = widgets.HTML()
        self.update_code_display(code_display, "")
        return code_display

    def create_input_widgets(self) -> Tuple[widgets.Text, widgets.Dropdown]:
        modelname_input = widgets.Text(
            value=self.default_modelname,
            description="Model Name",
            placeholder="eg. directory/name",
            layout=widgets.Layout(width="auto"),
        )
        model_universe_dropdown = widgets.Dropdown(
            options=AVAILABLE_MARKETS,
            value=self.default_model_universe,
            description="Universe",
            layout=widgets.Layout(width="auto"),
        )
        return modelname_input, model_universe_dropdown

    def create_action_widgets(
        self,
    ) -> Tuple[
        widgets.Button,
        widgets.Button,
        widgets.Button,
        widgets.Button,
        widgets.Button,
        widgets.IntProgress,
    ]:
        button_layout = widgets.Layout(width="auto", margin="0 5px")
        submit_button = widgets.Button(
            description="Submit",
            button_style="primary",
            layout=button_layout,
        )
        cancel_button = widgets.Button(
            description="Close",
            button_style="danger",
            layout=button_layout,
        )
        position_button = widgets.Button(
            description="Position",
            button_style="info",
            layout=button_layout,
        )

        simulation_button = widgets.Button(
            description="Simulation",
            button_style="info",
            layout=button_layout,
        )

        refresh_button = widgets.Button(
            description="Clear",
            button_style="warning",
            layout=button_layout,
        )

        progress = widgets.IntProgress(
            value=0,
            min=0,
            max=100,
            description="Loading",
            bar_style="info",
            orientation="horizontal",
            layout=widgets.Layout(width="100%", margin="0"),
        )

        for button in [
            submit_button,
            cancel_button,
            position_button,
            simulation_button,
        ]:
            button.add_class("widget-button")

        return (
            submit_button,
            cancel_button,
            position_button,
            simulation_button,
            refresh_button,
            progress,
        )

    def create_action_layout(self) -> widgets.VBox:
        button_box = widgets.HBox(
            [
                self.submit_button,
                self.position_button,
                self.simulation_button,
                self.refresh_button,
                self.cancel_button,
            ],
            layout=widgets.Layout(
                justify_content="flex-start", align_items="center", margin="0"
            ),
        )
        return widgets.VBox(
            [button_box, self.progress],
            layout=widgets.Layout(margin="0"),
        )

    def on_modelname_change(self, change):
        self.update_info_display()

    def colored_print(self, text: str, color: str):
        if isinstance(text, str):
            formatted_text = text.replace("\n", "<br>").replace(
                " ", "&nbsp;"
            )  # 줄바꿈과 공백을 HTML에 맞게 변경
        else:
            formatted_text = str(text)
        with self.status_output:
            display(HTML(f"<pre style='color: {color};'>{formatted_text}</pre>"))

    def update_info_display(self):
        modelname = self.model_name_input.value

        self.status_output.clear_output()
        if (
            modelname.startswith("/")
            or " " in modelname
            or "." in modelname
            or modelname.strip() == ""
        ):
            self.colored_print(
                "Error: Model name cannot start with '/' or contain spaces or '.'.",
                "red",
            )
            self.submit_button.disabled = True
            self.position_button.disabled = True
            self.simulation_button.disabled = True
        else:
            output_path = os.path.join(os.getcwd(), modelname, self.model_file_name)
            self.colored_print(f"Model will be saved to: {output_path}", "green")
            self.submit_button.disabled = False
            self.position_button.disabled = False
            self.simulation_button.disabled = False

        self.update_code_display(
            self.code_display,
            (
                output_path + f" ({self.model_type.lower()})"
                if "output_path" in locals()
                else ""
            ),
        )

    def update_code_display(self, code_display: widgets.HTML, file_path: str):
        formatter = HtmlFormatter(style="monokai")
        highlighted_code = highlight(self.model_cell.source, PythonLexer(), formatter)

        style = (
            MAC_STYLE + "<style>" + formatter.get_style_defs(".highlight") + "</style>"
        )
        html_content = f"""
        {style}
        <div class="mac-window" style="margin-top: 20px;">
            <div class="mac-titlebar">
                <div class="mac-buttons">
                    <div class="mac-button mac-close"></div>
                    <div class="mac-button mac-minimize"></div>
                    <div class="mac-button mac-zoom"></div>
                </div>
                <div class="mac-title" style="text-align: center; color: #fff; padding: 5px;">
                    {" " + file_path}
                </div>
            </div>
            <div class="mac-content" style="padding: 10px;">
                {highlighted_code}
            </div>
        </div>
        """
        code_display.value = html_content

    def submit(self, model_name=None, model_universe=None, gpu=None):
        self.reinitialize(model_name=model_name, model_universe=model_universe, gpu=gpu)
        with self.status_output:
            try:
                print("Submission preparation...")
                self.save_model_and_load_instance()
                self.submit_model()
            except Exception as e:
                self.handle_error("Submission", e, raise_error=True)

    def get_position(self, start_date, end_date):
        self.reinitialize(start_date=start_date, end_date=end_date)
        with self.status_output:
            try:
                self.validate_dates()
                print(
                    f"Getting position for period: {self.start_date_input.value} to {self.end_date_input.value}"
                )
                self.save_model_and_load_instance()
                self.get_and_validate_position()
                return self.position
            except Exception as e:
                self.handle_error("Position Validation", e, raise_error=True)

    def get_simulation(self, start_date, end_date):
        self.reinitialize(start_date=start_date, end_date=end_date)
        with self.status_output:
            try:
                self.validate_dates()
                print(
                    f"Running simulation for period: {self.start_date_input.value} to {self.end_date_input.value}"
                )
                self.save_model_and_load_instance()
                self.get_and_validate_position()
                self.run_simulation()
                print("Simulation completed successfully.")
                return self.simulation_result
            except Exception as e:
                self.handle_error("Simulation", e, raise_error=True)

    def on_position_click(self, b: Any) -> None:
        self.sidecar.close()
        with self.status_output:
            self.status_output.clear_output()
            self.start_progress()
            self.get_position(self.start_date_input.value, self.end_date_input.value)
            self.progress.value = 100
            self.progress.bar_style = "success"

    def on_submit(self, b: Any) -> None:
        self.sidecar.close()
        with self.status_output:
            self.status_output.clear_output()
            print("Submission preparation...")
            self.set_button_states(submit_disabled=True, cancel_disabled=True)
            self.progress.value = 0

            try:
                self.start_progress()
                self.submit()
            finally:
                self.set_button_states(submit_disabled=False, cancel_disabled=False)

    def on_simulation_click(self, b: Any) -> None:
        self.sidecar.close()
        with self.status_output:
            self.status_output.clear_output()
            self.start_progress()
            self.get_simulation(self.start_date_input.value, self.end_date_input.value)
            self.progress.value = 100
            self.progress.bar_style = "success"

    def reinitialize(
        self,
        start_date=None,
        end_date=None,
        model_name=None,
        model_universe=None,
        gpu=None,
    ) -> None:
        self.sidecar.close()
        self.__init__(
            start_date if start_date is not None else self.start_date_input.value,
            end_date if end_date is not None else self.end_date_input.value,
            model_name if model_name is not None else self.model_name_input.value,
            (
                model_universe
                if model_universe is not None
                else self.model_universe_dropdown.value
            ),
            gpu if gpu is not None else self.gpu_checkbox.value,
        )
        self.status_output.clear_output()

    def on_refresh(self, b: Any) -> None:
        self.sidecar.close()
        self.reinitialize()

    def validate_dates(self) -> None:
        start_date = self.start_date_input.value
        end_date = self.end_date_input.value
        if not start_date or not end_date:
            raise ValueError("Please enter both start and end dates.")
        if start_date > end_date:
            raise ValueError("Start date must be before end date.")

    def get_and_validate_position(self) -> None:
        self.position = self.model_instance.get(
            self.start_date_input.value, self.end_date_input.value
        )
        print("Position retrieved successfully.")
        print(self.position.sum(axis=1).tail())
        self.model_info = get_model_info(
            self.model_universe_dropdown.value, self.model_type
        )
        validator = ValidationHelper(
            model_path=self.model_name_input.value, model_info=self.model_info
        )
        validator.validate()

    def run_simulation(self) -> None:
        from finter.backtest.simulator import Simulator

        simulator = Simulator(self.model_universe_dropdown.value)
        results = simulator.run(
            self.position,
            start=self.start_date_input.value,
            end=self.end_date_input.value,
        )
        summary = results.summary
        self.simulation_result = summary
        self.plot_nav(summary)

    def plot_nav(self, summary: Any) -> None:
        import plotly.graph_objs as go

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=summary["nav"].index,
                y=summary["nav"].values,
                mode="lines",
                name="NAV",
            )
        )
        fig.update_layout(
            title="Simulation Results: NAV", xaxis_title="Date", yaxis_title="NAV"
        )
        display(fig)

    def check_name_exist(self) -> bool:
        return name_exist(
            self.model_type,
            self.model_universe_dropdown.value,
            self.model_name_input.value.split("/")[-1],
        )

    def save_model_and_load_instance(self):
        self.output_path = os.path.join(
            os.getcwd(), self.model_name_input.value, self.model_file_name
        )

        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        self.write_notebook(self.output_path)
        with self.status_output:
            print(f"Notebook saved to {self.output_path}")

        path_manager = FileManager()
        path_manager.clear_paths()
        self.model_instance = load_model_instance(self.output_path, self.model_type)
        path_manager.copy_files_to(self.model_name_input.value)

    def submit_model(self):
        self.model_info = get_model_info(
            self.model_universe_dropdown.value,
            self.model_type,
        )
        with self.status_output:
            print(
                f"Name: {self.model_name_input.value}, Universe: {self.model_universe_dropdown.value}, Type: {self.model_type.lower()}"
            )

        if self.check_name_exist():
            # if self.overwrite:
            #     self.colored_print("Warning: Overwriting existing model.", "orange")
            #     self.proceed_with_submission()
            # else:
            self.show_overwrite_dialog()
        else:
            self.proceed_with_submission()

    def show_overwrite_dialog(self):
        # self.status_output.clear_output()
        with self.status_output:
            print("Model name already exists. Do you want to overwrite?")
            overwrite_button = widgets.Button(
                description="Overwrite", button_style="warning"
            )
            cancel_button = widgets.Button(description="Close", button_style="danger")

            overwrite_button.on_click(lambda _: self.proceed_with_submission())
            cancel_button.on_click(lambda _: self.cancel_submission())

            display(widgets.HBox([overwrite_button, cancel_button]))
            self.progress.value = 100
            self.progress.bar_style = "danger"

    def proceed_with_submission(self):
        self.start_progress()

        with self.status_output:
            print("Submission started...")

            prepare_docker_submit_files(
                self.model_name_input.value,
                self.gpu_checkbox.value,
                self.image_dropdown.value,
            )

            # Perform validation
            try:
                self.model_info["gpu"] = self.gpu_checkbox.value

                if self.gpu_checkbox.value:
                    self.model_info["machine"] = self.machine_dropdown.value

                validator = ValidationHelper(
                    model_path=self.model_name_input.value, model_info=self.model_info
                )
                validator.validate()
            except Exception as e:
                self.handle_error("Validation", e, raise_error=True)

            # Todo insample, benchmark
            submit_result = submit_model(
                model_info=self.model_info,
                output_directory=self.model_name_input.value,
                docker_submit=True,  # docker_submit=False is deprecated
                staging=False,
            )
            if submit_result is None:
                self.handle_error("Submission", "Error submitting the model.")
            else:
                self.progress.value = 100
                self.progress.bar_style = "success"
                print("Submission completed!")
                print(f"Model ID: {submit_result.result['identity_name']}")
                print("Validation is in progress on the server.")
                display(
                    HTML(
                        f'<a href="{submit_result.s3_url}" target="_blank">Validation URL</a>'
                    )
                )

    def cancel_submission(self):
        self.status_output.clear_output()
        self.colored_print("Submission cancelled.", "orange")

    def handle_error(self, process: str, error: Exception, raise_error: bool = False):
        self.progress.bar_style = "danger"
        self.progress.value = 100
        self.colored_print(f"{process} failed: {str(error)}", "red")
        if raise_error:
            raise

    def on_cancel(self, b):
        self.sidecar.close()
        # with self.status_output:
        # clear_output(wait=True)
        # self.colored_print("Submission cancelled.", "orange")

    def set_button_states(self, submit_disabled: bool, cancel_disabled: bool):
        self.submit_button.disabled = submit_disabled
        self.cancel_button.disabled = cancel_disabled

    def start_progress(self):
        self.progress.value = 0
        self.progress.bar_style = "info"

        def progress_animation():
            direction = 1
            while True:
                self.progress.value += direction

                if self.progress.value > 95:
                    self.progress.value = 100
                    direction = 0
                    break

                if self.progress.value >= 90:
                    direction = -1
                elif self.progress.value <= 80:
                    direction = 1

                time.sleep(0.1)

        thread = threading.Thread(target=progress_animation)
        thread.start()
