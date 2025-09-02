import os

from finter.ai.gpt.summary_strategy import summary_strategy


def summary_strategy_after_submit(output_file_path):
    with open(output_file_path, "r") as f:
        input_text = f.read()

    summary_text = summary_strategy(input_text)

    file_directory = os.path.dirname(output_file_path)
    file_name = "summary.md"

    with open(os.path.join(file_directory, file_name), "w") as f:
        f.write(summary_text)
