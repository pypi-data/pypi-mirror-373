import os
from typing import Optional, Tuple

import nbformat
from IPython import get_ipython
from nbconvert import ScriptExporter

from finter.framework_model.submission.config import (
    ModelTypeConfig,
    get_output_path,
    validate_and_get_model_type_name,
)
from finter.settings import logger
from finter.utils.timer import timer


class NotebookExtractor:
    def __init__(self):
        self.model_cell, self.model_type, self.model_file_name = (
            self.extract_cells_with_class()
        )

    def extract_cells_with_class(self) -> Tuple[nbformat.NotebookNode, str, str]:
        notebook_path = get_ipython().user_ns["__session__"]
        with open(notebook_path, "r", encoding="utf-8") as notebook_file:
            notebook = nbformat.read(notebook_file, as_version=4)

        matching_cells = []
        for i, cell in enumerate(notebook.cells, 1):
            if "class Alpha" in cell.source and "class Portfolio" in cell.source:
                raise ValueError(
                    f"Cell {i} contains both 'class Alpha' and 'class Portfolio'. Please separate them into different cells."
                )
            elif "class Alpha" in cell.source:
                matching_cells.append((i, cell, "alpha"))
            elif "class Portfolio" in cell.source:
                matching_cells.append((i, cell, "portfolio"))
            elif "class FlexibleFund" in cell.source:
                matching_cells.append((i, cell, "flexible_fund"))

        if len(matching_cells) > 1:
            cell_numbers = ", ".join(str(i) for i, _, _ in matching_cells)
            raise ValueError(
                f"Found {len(matching_cells)} cells with 'class Alpha' or 'class Portfolio' in cell numbers: {cell_numbers}. Expected only one."
            )
        elif len(matching_cells) == 0:
            raise ValueError(
                "No cells containing 'class Alpha' or 'class Portfolio' were found."
            )

        model_type = validate_and_get_model_type_name(matching_cells[0][2])

        return (
            matching_cells[0][1],
            model_type,
            ModelTypeConfig[model_type].file_name,
        )  # Return the cell and the model type

    def write_notebook(self, output_path: str):
        extracted_notebook = nbformat.v4.new_notebook()
        extracted_notebook.cells = [self.model_cell]
        output_path = self.convert_notebook_to_script(extracted_notebook, output_path)

    def convert_notebook_to_script(
        self, notebook: nbformat.NotebookNode, output_path: str
    ) -> Optional[str]:
        """
        Converts a notebook object into a Python script and saves it to the specified path.

        Parameters:
        - notebook: Notebook object to convert.
        - output_path (str): Path to save the converted script.

        Returns:
        - output_path (str): Path to the converted script if successful, False otherwise.
        """
        exporter = ScriptExporter()

        try:
            body, resources = exporter.from_notebook_node(notebook)

            with open(output_path, "w", encoding="utf-8") as output_file:
                output_file.write(body)
        except Exception as e:
            logger.error(f"Error during conversion: {e}")
            raise

        return output_path


@timer
def extract_and_convert_notebook(current_notebook_name, model_name, model_type="alpha"):
    """
    Extracts specific cells containing a given class name from a notebook and converts them into a Python script.

    Parameters:
    - current_notebook_name (str): Name of the current notebook file (without .ipynb extension).
    - model_name (str): Directory to save the converted Python script.
    - model_type (str): Type of model (alpha or portfolio).

    Returns:
    - output_path (str): Path to the converted script if successful, False otherwise.
    """

    current_directory = os.getcwd()

    notebook_path = f"{current_notebook_name}.ipynb"
    output_path = get_output_path(model_name, model_type)

    if not current_notebook_name:
        logger.info("No notebook name provided. Skipping extraction and conversion.")
        return output_path

    class_declaration = f"class {ModelTypeConfig[model_type.upper()].class_name}"

    # Log directory
    logger.info(f"Current directory: {current_directory}")
    logger.info(f"Notebook path: {notebook_path}")
    logger.info(f"Output path: {output_path}")

    # Ensure the output directory exists
    os.makedirs(model_name, exist_ok=True)

    # Load the notebook
    try:
        with open(notebook_path, "r", encoding="utf-8") as notebook_file:
            notebook = nbformat.read(notebook_file, as_version=4)
    except IOError:
        logger.error(f"Error: Could not find {current_directory}/{notebook_path}")
        raise

    # Extract cells that contain the class_name
    try:
        extracted_cells = [
            cell for cell in notebook.cells if class_declaration in cell.source
        ]

        if not extracted_cells:
            logger.error(
                f"No cells containing the class name '{class_declaration}' were found."
            )
            raise Exception("No cells found with the specified class name")

        extracted_notebook = nbformat.v4.new_notebook()
        extracted_notebook.cells = extracted_cells
    except Exception as e:
        logger.error(f"Error while extracting cells: {e}")
        raise

    # Convert the notebook to a Python script
    output_path = convert_notebook_to_script(extracted_notebook, output_path)

    return output_path


def convert_notebook_to_script(notebook, output_path):
    """
    Converts a notebook object into a Python script and saves it to the specified path.

    Parameters:
    - notebook: Notebook object to convert.
    - output_path (str): Path to save the converted script.

    Returns:
    - output_path (str): Path to the converted script if successful, False otherwise.
    """
    exporter = ScriptExporter()

    try:
        body, resources = exporter.from_notebook_node(notebook)

        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write(body)
    except Exception as e:
        logger.error(f"Error during conversion: {e}")
        raise

    return output_path
