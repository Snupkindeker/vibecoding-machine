import base64
import requests

from dotenv import load_dotenv
from os import getenv


load_dotenv()
github_key = getenv("GITHUB_PAT")


def create_file(repo: str, path: str, content: str, message: str = None, branch: str = "main") -> dict:
    if not github_key:
        raise ValueError("The GitHub PAT is invalid. Please provide a valid GitHub PAT to the GITHUB_PAT environment variable.")

    try:
        check_url = f"https://api.github.com/repos/{repo}/contents/{path}"
        headers = {"Authorization": f"token {github_key}", "Accept": "application/vnd.github_tools.v3+json"}
        resp = requests.get(check_url, headers=headers)
        if resp.status_code == 200:
            raise FileExistsError(f"The {path} file already exists. Use write_file to rewrite it.")
        elif resp.status_code != 404:
            resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(e)

    # print("Step 1 success")

    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    payload = {
        "message": message or f"Create {path} via API",
        "content": encoded,
        "branch": branch
    }
    put_url = f"https://api.github.com/repos/{repo}/contents/{path}"
    resp_put = requests.put(put_url, headers=headers, json=payload)
    resp_put.raise_for_status()
    return resp_put.json()


if __name__ == "__main__":
    create_file("Snupkindeker/TestRepo", "test.txt", "Hi!")