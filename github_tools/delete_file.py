import requests

from dotenv import load_dotenv
from os import getenv


load_dotenv()
github_key = getenv("GITHUB_PAT")


def delete_file(repo: str, path: str, message: str = None, branch: str = "main") -> dict:
    if not github_key:
        raise ValueError("The GitHub PAT is invalid. Please provide a valid GitHub PAT to the GITHUB_PAT environment variable.")

    headers = {
        "Authorization": f"token {github_key}",
        "Accept": "application/vnd.github.v3+json"
    }

    get_url = f"https://api.github.com/repos/{repo}/contents/{path}"
    resp = requests.get(get_url, headers=headers)
    if resp.status_code == 404:
        raise Exception(f"File '{path}' not found in repository '{repo}'")
    elif resp.status_code != 200:
        resp.raise_for_status()

    file_data = resp.json()
    sha = file_data.get("sha")
    if not sha:
        raise Exception(f"Could not retrieve SHA for '{path}'")

    # 2. Удалить файл
    delete_url = f"https://api.github.com/repos/{repo}/contents/{path}"
    payload = {
        "message": message or f"Delete {path} via API",
        "sha": sha,
        "branch": branch
    }
    resp_delete = requests.delete(delete_url, headers=headers, json=payload)
    resp_delete.raise_for_status()
    return resp_delete.json()


if __name__ == "__main__":
    try:
        result = delete_file("Snupkindeker/TestRepo", "test.txt")
        print("File deleted successfully:")
        print(result)
    except Exception as e:
        print("Error:", e)