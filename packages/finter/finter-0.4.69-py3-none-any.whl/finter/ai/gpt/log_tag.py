import requests

from finter.ai.gpt.config import URL_NAME


def log_tag(input_text):
    url = f"http://{URL_NAME}:8282/log_tag"
    data = {"input": input_text}

    response = requests.post(url, json=data)
    return response.json()


if __name__ == "__main__":
    input_text = """
    """
    rel = log_tag(input_text)
    print(rel)
