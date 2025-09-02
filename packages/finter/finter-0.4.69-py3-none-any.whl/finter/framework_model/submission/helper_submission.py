import finter
from finter.settings import get_api_client, logger
from finter.utils.timer import timer


@timer
def submit_model(model_info, output_directory, docker_submit, staging, model_nickname=None):
    """
    Submits the model to the Finter platform.

    :param model_info: Information about the model to submit.
    :param output_directory: Directory containing the model output files.
    :param docker_submit: Whether to submit the model using Docker.
    :return: The result of the submission if successful, None otherwise.
    """
    try:
        res = finter.SubmissionApi(get_api_client()).submission_create(
            model_info, output_directory, docker_submit, staging, model_nickname
        )
        return res
    except Exception as e:
        logger.error(f"Error submitting the model: {e}")
        return None
