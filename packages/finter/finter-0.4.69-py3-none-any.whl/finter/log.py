import json
from datetime import datetime

import requests

URL = "https://log.monitoring.finter.quantit.io/log"


class PromtailLogger:
    @staticmethod
    def send_log(level, message, service, user_id, operation, status):
        timestamp = datetime.now().isoformat() + "Z"

        log_data = {
            "timestamp": timestamp,
            "level": level,
            "message": message,
            "service": service,
            "details": {
                "user_id": user_id,
                "operation": operation,
                "status": status,
            },
        }

        try:
            response = requests.post(
                URL,
                data=json.dumps(log_data),
                headers={"Content-Type": "application/json"},
            )
        except Exception:
            pass

        # if response.status_code == 200:
        #     print("Log sent successfully")
        # else:
        #     print(f"Failed to send log: {response.status_code} - {response.text}")

    @staticmethod
    def get_user_info():
        import os

        from dotenv import load_dotenv

        load_dotenv()

        user_name = os.environ.get("FINTER_USER")
        email = os.environ.get("FINTER_GROUP")
        group_name = os.environ.get("FINTER_EMAIL")
        user_id = f'{{"username": "{user_name}", "email": "{email}", "group": "{group_name}"}}'
        return user_id


if __name__ == "__main__":
    PromtailLogger.send_log(
        level="INFO",
        message="test_messsage",
        service="test_finter",
        user_id="test_user",
        operation="test_operation",
        status="success",
    )
