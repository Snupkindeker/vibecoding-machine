import requests

from dotenv import load_dotenv
from os import getenv


load_dotenv()
github_key = getenv("GITHUB_PAT")


def get_file_list(repo: str, path: str = "") -> dict:
    if not github_key:
        raise ValueError("Invalid GitHub PAT.")

    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"token {github_key}", "Accept": "application/vnd.github.v3+json"}
    resp = requests.get(url, headers=headers)

    if resp.status_code == 404:
        if path == "":
            return {"files": []}
        else:
            return {"error": f"Path '{path}' not found"}

    resp.raise_for_status()
    items = resp.json()
    result = []
    for item in items:
        if item["type"] == "file":
            result.append(item["name"])
        elif item["type"] == "dir":
            sub = get_file_list(repo, item["path"])
            if "error" in sub:
                return sub
            result.append({item["name"]: sub.get("files", [])})
    return {"files": result}


if __name__ == "__main__":
    print(get_file_list("Snupkindeker/Ultimathe", "."))