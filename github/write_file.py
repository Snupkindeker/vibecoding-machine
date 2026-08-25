import base64
import requests

from dotenv import load_dotenv
from os import getenv


load_dotenv()
github_key = getenv("GITHUB_PAT")


def write_file(repo: str, path: str, content: str, message: str = None) -> dict:
    if not github_key:
        raise ValueError("Токен не найден")

    # Кодируем содержимое в base64
    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    # Получаем SHA текущего файла, если он существует
    sha = None
    get_url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"token {github_key}", "Accept": "application/vnd.github.v3+json"}
    resp = requests.get(get_url, headers=headers)
    if resp.status_code == 200:
        sha = resp.json().get("sha")
    elif resp.status_code != 404:
        resp.raise_for_status()  # другая ошибка

    # Формируем payload для PUT
    if message is None:
        message = f"Update {path} via API" if sha else f"Create {path} via API"

    payload = {
        "message": message,
        "content": encoded,
        "branch": "main"   # можно сделать параметром, но для простоты фиксируем
    }
    if sha:
        payload["sha"] = sha

    put_url = f"https://api.github.com/repos/{repo}/contents/{path}"
    resp_put = requests.put(put_url, headers=headers, json=payload)
    resp_put.raise_for_status()
    return resp_put.json()


if __name__ == "__main__":
    write_file("Snupkindeker/vibecoding-machine", "eggs/test.txt", "print('Hi!'")