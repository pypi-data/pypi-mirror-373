import os
import re

import requests
from dotenv import load_dotenv

from finter.api.alpha_api import AlphaApi
from finter.api_client import ApiClient
from finter.framework_model.submission.config import (
    get_model_info,
    validate_and_get_benchmark_name,
    validate_and_get_model_type_name,
)
from finter.framework_model.submission.helper_github import commit_folder_to_github
from finter.framework_model.submission.helper_notebook import (
    extract_and_convert_notebook,
)
from finter.framework_model.submission.helper_path import FileManager
from finter.framework_model.submission.helper_poetry import prepare_docker_submit_files
from finter.framework_model.submission.helper_position import (
    load_and_get_position,
    load_model_instance,
)
from finter.framework_model.submission.helper_simulation import Simulation
from finter.framework_model.submission.helper_submission import submit_model
from finter.framework_model.submission.helper_summary_strategy import (
    summary_strategy_after_submit,
)
from finter.framework_model.submission.helper_ui import SubmissionUI
from finter.framework_model.validation import ValidationHelper
from finter.settings import (
    log_section,
    log_warning,
    log_with_traceback,
    log_with_user_event,
)


def name_exist(model_type, model_universe, model_name):
    load_dotenv()
    check_url = "https://api.finter.quantit.io/user_info?item=username"
    check_header = {
        "accept": "application/json",
        "Authorization": f"Token {os.environ.get('FINTER_API_KEY')}",
    }
    try:
        user_name = requests.get(check_url, headers=check_header).json()["data"]
    except:
        log_with_user_event(
            "position_extraction_success",
            "finter",
            "notebook_submission",
            "position",
            log_type="error",
            log_message="Get user name failed.",
        )
        return False

    try:
        am_list = (
            AlphaApi(ApiClient()).alpha_identities_retrieve().am_identity_name_list
        )
    except:
        log_with_user_event(
            "position_extraction_success",
            "finter",
            "notebook_submission",
            "position",
            log_type="error",
            log_message="Get model list failed.",
        )
        return False

    check_list = [user_name, model_type.lower()]

    if model_universe == "kr_stock":
        check_list.extend(["krx", "stock"])
    elif model_universe == "us_etf":
        check_list.extend(["us", "compustat", "etf"])
    elif model_universe == "us_stock":
        check_list.extend(["us", "compustat", "stock"])
    elif model_universe == "us_future":
        check_list.extend(["us", "bloomberg", "future"])
    elif model_universe == "vn_stock":
        check_list.extend(["vnm", "fiintek", "stock"])
    elif model_universe == "id_stock":
        check_list.extend(["id", "compustat", "stock"])
    elif model_universe == "btcusdt_spot_binance":
        check_list.extend(["crypto", "binance", "spot"])

    # 모든 check_list 요소들이 am에 포함되어 있는지 확인
    own_am_list = [
        am.split(".")[-1]
        for am in am_list
        if all(element in am.split(".") for element in check_list)
    ]

    if model_name in own_am_list:
        return True
    return False


class NotebookSubmissionHelper:
    """
    A helper class to facilitate the submission process of financial models
    developed in Jupyter Notebooks. It supports extracting relevant cells from a
    notebook, running simulations, performing validations, and submitting the model
    for further use or evaluation.

    Attributes:
        notebook_name (str): The name of the notebook file (including path if necessary).
        model_name (str): The path where the model will be saved. The last part of the path is considered the name of the model. For example, 'path/to/model_name' would save the model in the 'path/to/' directory with 'model_name' as the model name.
        model_universe (str): The universe for the model (e.g. "kr_stock").
        model_type (str): The type of the model (e.g. "alpha" or "portfolio").
        benchmark (str): The benchmark to use for the model. Default is None. If not specified, the default benchmark for the model universe will be used. If False, no benchmark will be used.
    """

    def __init__(
        self,
        notebook_name,
        model_name,
        model_universe,
        model_type="alpha",
        benchmark=None,
        use_cli=False,
        **kwargs,
    ):
        """
        Initializes the NotebookSubmissionHelper with necessary information.

        Args:
            notebook_name (str): The name of the notebook file (including path if necessary).
            model_name (str): The path where the model will be saved. The last part of the path is considered the name of the model. This allows for specifying the directory to save the model along with the model's name. For example, 'path/to/model_name' would save the model in the 'path/to/' directory with 'model_name' as the model name.
            model_universe (str): The universe for the model (e.g. "kr_stock").
            model_type (str): The type of the model (e.g. "alpha" or "portfolio").
            benchmark (str): The benchmark to use for the model. Default is None. If not specified, the default benchmark for the model universe will be used. If False, no benchmark will be used.
        """
        log_warning(
            "!!! IMPORTANT: Please ensure your current notebook is SAVED before proceeding with the submission process. !!!"
        )

        self.notebook_name = notebook_name
        self.model_name = model_name
        self.model_universe = model_universe

        self.model_info = get_model_info(model_universe, model_type)

        if "insample" in kwargs:
            insample = kwargs.pop("insample")

            if not re.match(r"^\d+ days$", insample):
                raise ValueError("insample should be like '100 days'")

            self.model_info["insample"] = insample
            if kwargs:
                log_warning(f"Unused parameters: {kwargs}")

        self.model_type = validate_and_get_model_type_name(model_type)
        self.benchmark = validate_and_get_benchmark_name(model_universe, benchmark)

        # Extract and convert the notebook
        log_section("Notebook Extraction")
        self.output_file_path = extract_and_convert_notebook(
            self.notebook_name,
            self.model_name,
            model_type=self.model_type,
        )

        if not self.output_file_path:
            log_with_user_event(
                "notebook_extraction_error",
                "finter",
                "notebook_submission",
                "notebook",
                log_type="error",
                log_message="Error extracting notebook.",
            )
            return

        log_with_user_event(
            "notebook_extraction_success",
            "finter",
            "notebook_submission",
            "notebook",
            log_type="info",
            log_message=f"Notebook extracted to {self.output_file_path}",
        )

        path_manager = FileManager()
        path_manager.clear_paths()
        self.model_instance = load_model_instance(self.output_file_path, model_type)
        path_manager.copy_files_to(self.model_name)

        try:
            self.display(use_cli=use_cli)
        except Exception as e:
            log_warning(f"Error while displaying file content: {e}")
        if use_cli:
            self.process(1, 1, submit=True)

    def process(
        self,
        start: int,
        end: int,
        position=False,
        simulation=False,
        validation=False,
        submit=False,
        git=False,
        docker_submit=True,
        staging=False,
    ):
        """
        Processes the notebook by extracting specified cells, and optionally running position extraction, simulation, validation, and submission steps. Validation is automatically performed if submission is requested. Position extraction is mandatory for simulation.

        Args:
            start (int): The start date for the simulation and validation processes.
            end (int): The end date for the simulation and validation processes.
            position (bool): Flag to determine whether to extract positions from the model. Default is False.
            simulation (bool): Flag to determine whether to run a simulation based on the extracted positions. Default is False.
            validation (bool): Flag to determine whether to validate the model. Default is False.
            submit (bool): Flag to determine whether to submit the model. Default is False.
            git (bool): Flag to determine whether to commit the model to GitHub. Default is False.
            docker_submit (bool): Flag to determine whether to submit the model using Docker. False will use legacy submit. Default is True.
            staging (bool): Flag to determine whether to use staging docker submit pipeline. Defalut is False.
        """

        # Ensure position extraction if simulation is requested
        if simulation and not position:
            position = True
            log_warning(
                "Position extraction is required for simulation. Setting position=True."
            )

        # Perform position extraction if required
        if position:
            log_section("Position Extraction")

            self.position = load_and_get_position(
                start, end, self.output_file_path, model_type=self.model_type
            )
            if self.position is None:
                log_with_user_event(
                    "position_extraction_error",
                    "finter",
                    "notebook_submission",
                    "position",
                    log_type="error",
                    log_message="Error extracting positions from notebook.",
                )
                raise ValueError("Error extracting positions from notebook.")

            log_with_user_event(
                "position_extraction_success",
                "finter",
                "notebook_submission",
                "position",
                log_type="info",
                log_message="Position extraction from notebook ran successfully.",
            )

        # Run simulation with the extracted positions if requested
        if simulation:
            self.model_stat = Simulation(
                model_universe=self.model_universe,
                model_type=self.model_type,
                position=self.position,
                benchmark=self.benchmark,
            ).run(start, end)

        # Validate the model if requested
        if validation:
            log_warning(
                "Validation is deprecated and will be removed in future versions."
            )
            # log_section("Validation")

            # try:
            #     validator = ValidationHelper(
            #         model_path=self.model_name, model_info=self.model_info
            #     )
            #     validator.validate()
            # except Exception as e:
            #     log_with_user_event(
            #         "model_validation_error",
            #         "finter",
            #         "notebook_submission",
            #         "validation",
            #     )
            #     log_with_traceback(f"Error validating the model: {e}")
            #     raise

            # log_with_user_event(
            #     "model_validation_success",
            #     "finter",
            #     "notebook_submission",
            #     "validation",
            #     log_type="info",
            #     log_message="Model validation completed successfully.",
            # )

        if docker_submit:
            prepare_docker_submit_files(self.model_name, gpu=None, image=None)
            submit = True
            log_warning("Docker submit is enabled. Setting submit=True.")

        # Submit the model if requested
        if submit:
            log_section("Model Submission")
            model_name = self.model_name.split("/")[-1]
            if name_exist(self.model_type, self.model_universe, model_name):
                self.submission_ui.show_resubmit_dialog(
                    self, model_name, docker_submit, staging
                )
                return  # Add this line to prevent further execution
            else:
                self.submit_model(docker_submit, staging)

        # Commit the model to GitHub if requested
        if git:
            log_section("GitHub Commit")
            try:
                commit_folder_to_github(folder_path=self.model_name)
            except Exception as e:
                log_with_user_event(
                    "model_commit_error",
                    "finter",
                    "notebook_submission",
                    "github",
                    log_type="error",
                    log_message="Error committing the model to GitHub.",
                )
                log_with_traceback(f"Error committing the model to GitHub: {e}")
                raise
            log_with_user_event(
                "model_commit_success",
                "finter",
                "notebook_submission",
                "github",
                log_type="info",
                log_message="Model committed to GitHub successfully.",
            )

    def submit_model(self, docker_submit, staging):
        log_section("Validation")

        try:
            validator = ValidationHelper(
                model_path=self.model_name, model_info=self.model_info
            )
            validator.validate()
        except Exception:
            log_with_user_event(
                "model_validation_error",
                "finter",
                "notebook_submission",
                "validation",
            )
            # log_with_traceback(f"Error validating the model: {e}")
            raise

        log_with_user_event(
            "model_validation_success",
            "finter",
            "notebook_submission",
            "validation",
            log_type="info",
            log_message="Model validation completed successfully.",
        )

        log_section("Model Submission")
        self.submit_result = submit_model(
            self.model_info, self.model_name, docker_submit, staging
        )
        if self.submit_result is None:
            log_with_user_event(
                "model_submission_error",
                "finter",
                "notebook_submission",
                "submission",
                log_type="error",
                log_message="Error submitting the model.",
            )
            return
        log_with_user_event(
            "model_submission_success",
            "finter",
            "notebook_submission",
            "submission",
            log_type="info",
            log_message="Model submitted successfully.",
        )

        log_with_user_event(
            "model_submission_success",
            "finter",
            "notebook_submission",
            "submission",
            log_type="info",
            log_message=f"Log file: {self.submit_result.s3_url}",
        )

        # Test the summary strategy after submission
        try:
            summary_strategy_after_submit(self.output_file_path)
        except Exception:
            pass

    def display(self, use_cli=False):
        self.submission_ui = SubmissionUI(self)
        if not use_cli:
            self.submission_ui.display_ui()
