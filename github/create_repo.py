import requests

from dotenv import load_dotenv
from os import getenv


load_dotenv()
github_key = getenv("GITHUB_PAT")


def create_repo(name: str, public: bool = False) -> dict:
    if not github_key:
        raise ValueError("Не передан GitHub токен и не установлена переменная окружения GITHUB_TOKEN")

    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {github_key}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
            "name": name,
            "private": not public
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()