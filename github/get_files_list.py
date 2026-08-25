import requests

from dotenv import load_dotenv
from os import getenv


load_dotenv()
github_key = getenv("GITHUB_PAT")


def get_file_list(repo: str, path: str = "") -> list:
    if not github_key:
        raise ValueError("Токен не найден")

    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"token {github_key}", "Accept": "application/vnd.github.v3+json"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    items = resp.json()

    result = []
    for item in items:
        if item["type"] == "file":
            result.append(item["name"])
        elif item["type"] == "dir":
            sub_items = get_file_list(repo, item["path"])
            result.append({item["name"]: sub_items})
    return result


if __name__ == "__main__":
    print(get_file_list("Snupkindeker/Ultimathe", "."))