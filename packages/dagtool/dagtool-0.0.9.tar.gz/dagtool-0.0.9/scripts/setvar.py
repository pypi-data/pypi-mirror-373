import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from httpx import BasicAuth

load_dotenv(str((Path(__file__).parent.parent / ".env").resolve()))


def set_variable(password: str):
    auth = BasicAuth(username="admin", password=password)
    client = httpx.Client(
        base_url="http://127.0.0.1:8080",
        auth=auth,
    )
    try:
        response = client.post(
            url="api/v1/variables",
            headers={"content-type": "application/json"},
            json={
                "key": "my_json_var",
                "value": '{"key1":"val1","key2":"123"}',
                "description": "test",
            },
        )
        response.raise_for_status()
        data = response.json()
        print(data)
    except httpx.HTTPStatusError as e:
        print(f"Got the error when update variable: {e}")
    except httpx.RequestError as e:
        print(f"Got the request error: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    pwd: str | None = os.getenv("AIRFLOW_ADMIN_PASSWORD")
    if pwd is None:
        raise ValueError("Does not get admin password from env var.")
    set_variable(pwd)
