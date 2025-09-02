import sys

import requests

from finter.ai.gpt.config import URL_NAME


def generate_cm_docs(input_text):
    url = f"http://{URL_NAME}:8282/cm-docs"
    data = {"input": input_text}
    response = requests.post(url, json=data)
    return response.json()["result"]


if __name__ == "__main__":
    # input_text = "content.fnguide.ftp.price_volume.*.1d"
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else ""
    rel = generate_cm_docs(user_prompt)
    for i in rel:
        print(i["response"])
