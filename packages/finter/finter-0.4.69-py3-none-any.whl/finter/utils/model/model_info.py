import os

import requests
from dotenv import load_dotenv

load_dotenv()


class ModelInfo:
    def __init__(self):
        self.url = "https://api.finter.quantit.io/model/model_info"
        self.headers = {
            "accept": "application/json",
            "Authorization": f'Token {os.environ.get("FINTER_API_KEY")}',
        }

    def get_model_info(self, model_name):
        response = requests.get(
            self.url, params={"identity_name": model_name}, headers=self.headers
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get model info: {response.text}")


if __name__ == "__main__":
    model_info = ModelInfo()
    print(model_info.get_model_info("portfolio.us.us.stock.shum.aristo1"))
