import sys

import requests

from finter.ai.gpt.config import URL_NAME


def get_file_content(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()
    return file_content


def generate_cookbook(file_path=""):
    url = f"http://{URL_NAME}:8282/cookbook"
    input_text = get_file_content(file_path)

    data = {"input": input_text}
    response = requests.post(url, json=data)
    return response.json()["result"]


if __name__ == "__main__":
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else ""
    rel = generate_cookbook(user_prompt)
    print(rel)
