import base64
import json
import os

import requests
from finter.framework_model.submission.helper_github_config import get_env_variable
from finter.settings import logger


def encode_content(file_path):
    """Encode file content to base64."""
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")


def get_file_sha(api_url, headers):
    """Retrieve the current SHA of a file in the repository, if it exists."""
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json().get("sha")
    return None


def commit_file_to_github(
    file_path, file_content, repo_owner, repo_name, branch_name, access_token
):
    """Commit a file to GitHub, handling both creation and update cases with error handling."""
    # Construct the GitHub API URL for the file.
    api_url = (
        f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    )
    headers = {"Authorization": f"token {access_token}"}

    try:
        # Check if the file already exists and get its SHA if it does.
        sha = get_file_sha(api_url, headers)

        data = {
            "message": f"Update {file_path}",
            "content": file_content,
            "branch": branch_name,
        }

        if sha:
            # Prompt to confirm modification if the file already exists.
            should_modify = input(
                f"The file {file_path} already exists. Modify it? (y/n): "
            )
            if should_modify.lower() != "y":
                logger.info(f"Skipping {file_path}")
                return
            data["sha"] = sha

        # Send the request to GitHub API.
        response = requests.put(api_url, headers=headers, data=json.dumps(data))

        if response.status_code in [200, 201]:
            logger.info(f"Successfully committed {file_path}")
        else:
            # Handle API error messages.
            error_message = response.json().get("message", "Unknown error occurred.")
            logger.error(f"Failed to commit {file_path}: {error_message}")

    except requests.exceptions.RequestException as e:
        # Handle network errors.
        logger.error(f"Request failed: {e}")

    except Exception as e:
        # Handle other unexpected errors.
        logger.error(f"An unexpected error occurred: {e}")


def commit_folder_to_github(folder_path):
    """Commit all files in a folder to GitHub, excluding __pycache__ and hidden directories."""
    # Retrieve GitHub configuration from environment variables.
    repo_owner = get_env_variable("GITHUB_REPO_OWNER")
    repo_name = get_env_variable("GITHUB_REPO_NAME")
    branch_name = get_env_variable("GITHUB_BRANCH_NAME")
    access_token = get_env_variable("GITHUB_ACCESS_TOKEN")

    for root, dirs, files in os.walk(folder_path):
        # Exclude __pycache__ and hidden directories.
        dirs[:] = [d for d in dirs if d != "__pycache__" and not d.startswith(".")]
        for file in files:
            if file.startswith("."):
                continue  # Skip hidden files.
            file_path = os.path.join(root, file)
            encoded_content = encode_content(file_path)

            logger.info(f"Committing {file_path} to GitHub")
            commit_file_to_github(
                file_path,
                encoded_content,
                repo_owner,
                repo_name,
                branch_name,
                access_token,
            )
