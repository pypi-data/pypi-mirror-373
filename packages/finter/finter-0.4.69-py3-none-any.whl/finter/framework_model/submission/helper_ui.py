import os
import threading
import time

from IPython.display import FileLink, clear_output, display
from ipywidgets import widgets
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

# Global CSS style
MAC_STYLE = """
<style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
    }
    .mac-window {
        background-color: #1e1e1e;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        margin: 20px 0;
        overflow: hidden;
        font-family: 'SF Mono', 'Menlo', 'Monaco', 'Courier', monospace;
    }
    .mac-titlebar {
        background: linear-gradient(to bottom, #3a3a3a, #2d2d2d);
        height: 28px;
        padding: 8px 12px;
        display: flex;
        align-items: center;
    }
    .mac-buttons {
        display: flex;
        gap: 8px;
    }
    .mac-button {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        border: none;
    }
    .mac-close { background-color: #ff5f56; }
    .mac-minimize { background-color: #ffbd2e; }
    .mac-zoom { background-color: #27c93f; }
    .mac-content {
        padding: 15px;
        overflow-x: auto;
        max-height: 400px;
        overflow-y: auto;
        background-color: #2D2D2D;
    }
    .mac-content pre {
        margin: 0;
        padding: 10px;
        font-size: 13px;
        line-height: 1.5;
        white-space: pre-wrap;
        word-wrap: break-word;
        background-color: #2D2D2D;
    }
    .mac-content::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    .mac-content::-webkit-scrollbar-thumb {
        background: #5a5a5a;
        border-radius: 6px;
        border: 3px solid #2D2D2D;
    }
    .mac-content::-webkit-scrollbar-track {
        background: #2D2D2D;
    }
    .widget-button {
        border-radius: 6px;
        font-size: 14px;
        padding: 6px 16px;
        border: none;
        color: white;
        transition: all 0.3s ease;
        font-weight: 500;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 32px;
        line-height: 1;
    }
    .widget-button.primary {
        background-color: #007aff;
    }
    .widget-button.primary:hover {
        background-color: #0056b3;
    }
    .widget-button.danger {
        background-color: #ff3b30;
    }
    .widget-button.danger:hover {
        background-color: #d9534f;
    }
    .widget-button.warning {
        background-color: #ff9500;
    }
    .widget-button.warning:hover {
        background-color: #f0ad4e;
    }
    .widget-hbox {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .widget-progress {
        height: 8px;
        border-radius: 4px;
        background-color: #e9ecef;
        overflow: hidden;
    }
    .widget-progress .progress-bar {
        height: 100%;
        background-color: #007aff;
        border-radius: 4px;
        transition: width 0.3s ease;
    }
</style>
"""


class SubmissionUI:
    def __init__(self, submission_helper):
        self.submission_helper = submission_helper
        self.status_output = widgets.Output()
        self.submit_button = widgets.Button(
            description="Submit",
            button_style="primary",
        )
        self.cancel_button = widgets.Button(
            description="Cancel",
            button_style="danger",
        )
        self.progress = widgets.IntProgress(
            value=0,
            min=0,
            max=100,
            description="Loading:",
            bar_style="info",
            orientation="horizontal",
            layout=widgets.Layout(width="50%"),
        )

        self.submit_button.add_class("widget-button")
        self.cancel_button.add_class("widget-button")

        self.submit_button.on_click(self.on_submit)
        self.cancel_button.on_click(self.on_cancel)

        self.main_output = widgets.Output()
        self.resubmit_output = widgets.Output()

    def display_ui(self):
        with self.main_output:
            clear_output(wait=True)
            file_path = self.submission_helper.output_file_path
            if not os.path.exists(file_path):
                display(
                    widgets.HTML(
                        value=f"<p>Error: File '{file_path}' does not exist.</p>"
                    )
                )
                return

            file_link = FileLink(
                file_path,
                result_html_prefix="Check the generated Python script: ",
                result_html_suffix="<br>If something went wrong, <strong style='color: #ff3b30;'>Please save the notebook</strong> and try again.",
            )
            display(file_link)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    file_content = f.read()
            except Exception as e:
                display(widgets.HTML(value=f"<p>File reading error: {str(e)}</p>"))
                return

            formatter = HtmlFormatter(style="monokai")
            highlighted_code = highlight(file_content, PythonLexer(), formatter)

            style = (
                MAC_STYLE
                + "<style>"
                + formatter.get_style_defs(".highlight")
                + "</style>"
            )
            html_content = f"""
            {style}
            <div class="mac-window">
                <div class="mac-titlebar">
                    <div class="mac-buttons">
                        <div class="mac-button mac-close"></div>
                        <div class="mac-button mac-minimize"></div>
                        <div class="mac-button mac-zoom"></div>
                    </div>
                </div>
                <div class="mac-content">
                    {highlighted_code}
                </div>
            </div>
            """
            display(widgets.HTML(value=html_content))
            ui = widgets.VBox(
                [
                    widgets.HBox(
                        [self.submit_button, self.cancel_button, self.progress],
                        layout=widgets.Layout(
                            justify_content="flex-start", align_items="center"
                        ),
                    ),
                    self.status_output,
                ]
            )
            display(ui)

        display(self.main_output)

    def on_submit(self, b):
        self.status_output.clear_output()
        self.submit_button.disabled = True
        self.cancel_button.disabled = True
        self.progress.value = 0

        with self.status_output:
            print("Submitting model...")
            try:
                self.start_progress()
                self.submission_helper.process(1, 1, submit=True)
                self.progress.value = 100
            except Exception as e:
                self.progress.bar_style = "danger"
                self.progress.value = 100
                print(f"\nSubmission failed: {str(e)}")
            finally:
                self.submit_button.disabled = False
                self.cancel_button.disabled = False

    def start_progress(self):
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

    def on_cancel(self, b):
        with self.main_output:
            clear_output(wait=True)
            print("Submission cancelled.")

    @staticmethod
    def show_resubmit_dialog(submission_helper, model_name, docker_submit, staging):
        resubmit_button = widgets.Button(
            description="Overwrite",
            button_style="warning",
            # layout=widgets.Layout(width="auto"),
        )
        cancel_button = widgets.Button(
            description="Cancel",
            button_style="danger",
            # layout=widgets.Layout(width="auto"),
        )
        output = widgets.Output()
        progress = widgets.IntProgress(
            value=0,
            min=0,
            max=100,
            description="Loading:",
            bar_style="info",
            orientation="horizontal",
            layout=widgets.Layout(width="50%"),
        )

        resubmit_button.add_class("widget-button")
        cancel_button.add_class("widget-button")

        def start_progress():
            def progress_animation():
                direction = 1  # 1이면 증가, -1이면 감소
                while True:
                    progress.value += direction

                    if progress.value > 95:  # 95 이상인 경우
                        progress.value = 100  # progress를 100으로 설정
                        direction = 0  # 애니메이션 중지
                        break
                    
                    if progress.value >= 90:  # 90 이상인 경우
                        direction = -1  # 감소 방향으로 전환
                    elif progress.value <= 80:  # 80 이하인 경우
                        direction = 1  # 증가 방향으로 전환

                    time.sleep(0.1)

            thread = threading.Thread(target=progress_animation)
            thread.start()

        def on_resubmit_click(b):
            resubmit_button.disabled = True
            cancel_button.disabled = True
            progress.value = 0
            start_progress()

            with output:
                print(f"Overwriting model '{model_name}'...")
                try:
                    submission_helper.submit_model(docker_submit, staging)
                    progress.value = 100
                except Exception as e:
                    progress.bar_style = "danger"
                    progress.value = 100
                    print(f"Overwrite failed: {str(e)}")
                finally:
                    resubmit_button.disabled = False
                    cancel_button.disabled = False

        resubmit_button.on_click(on_resubmit_click)
        cancel_button.on_click(submission_helper.submission_ui._on_cancel_click)

        print(f"Model '{model_name}' already exists.")
        # display(widgets.HTML(MAC_STYLE))

        with submission_helper.submission_ui.main_output:
            clear_output(wait=True)

        with submission_helper.submission_ui.resubmit_output:
            display(
                widgets.VBox(
                    [
                        widgets.HBox(
                            [resubmit_button, cancel_button, progress],
                            layout=widgets.Layout(
                                justify_content="flex-start", align_items="center"
                            ),
                        ),
                        output,
                    ]
                )
            )
        display(submission_helper.submission_ui.resubmit_output)

    def _on_cancel_click(self, b):
        with self.resubmit_output:
            clear_output()
        with self.main_output:
            clear_output()
            print("Submission cancelled.")
