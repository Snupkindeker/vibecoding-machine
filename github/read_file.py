import base64
import requests

from dotenv import load_dotenv
from os import getenv


load_dotenv()
github_key = getenv("GITHUB_PAT")


def read_file(repo: str, path: str) -> str:
    if not github_key:
        raise ValueError("The GitHub PAT is invalid. Please provide a valid GitHub PAT to the GITHUB_PAT environment variable.")

    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"token {github_key}", "Accept": "application/vnd.github.v3+json"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()

    if "content" not in data:
        raise ValueError("The file is too big.")
    content = base64.b64decode(data["content"]).decode("utf-8")
    return content


if __name__ == "__main__":
    print(read_file("Snupkindeker/Ultimathe", ".gitignore"))
    print(read_file("Snupkindeker/Ultimathe", "Cache/Cache.py"))