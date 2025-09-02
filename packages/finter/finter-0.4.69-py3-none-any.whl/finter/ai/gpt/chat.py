import requests

LMSYS_URL = "https://lmsys-be.finter.bot/llm/"
AVAILABLE_MODELS = ["gpt4o", "sonnet3.5", "gemini1.5-pro", "llama3-8b"]


def chat_gpt(input_text, model="gpt4o"):
    if model not in AVAILABLE_MODELS:
        raise ValueError(f"Invalid model. Choose from: {', '.join(AVAILABLE_MODELS)}")

    headers = {"Content-Type": "application/json"}
    data = {"text": input_text, "model": model}

    response = requests.post(LMSYS_URL, json=data, headers=headers)
    response.raise_for_status()  # Raises an exception for 4xx/5xx status codes
    return response.json()


if __name__ == "__main__":
    input_text = "안녕 넌 이름이 뭐니?"
    model = "gpt4o"  # You can change this to any of the available models
    result = chat_gpt(input_text, model)
    print(result)
