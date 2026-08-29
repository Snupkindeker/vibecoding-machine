import json
import requests
import sys
import os
import base64

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
langs_path = os.path.join(current_dir, 'langs.json')

if current_dir not in sys.path:
    sys.path.append(current_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)

licenses_path = os.path.join(root_dir, 'licenses')


from dotenv import load_dotenv
from os import getenv

from github_tools.create_file import create_file
from github_tools.create_repo import create_repo
from github_tools.delete_file import delete_file
from github_tools.get_file_list import get_file_list
from github_tools.read_file import read_file
from github_tools.write_file import write_file


load_dotenv()


def web_search(query: str) -> dict[str, str] | str:
    url = "https://api.langsearch.com/v1/web-search"
    key = getenv("LANGSEARCH_KEY")

    payload = json.dumps({
        "query": query,
        "freshness": "noLimit",
        "summary": True,
        "count": 3
    })
    headers = {
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }
    try:
        response: dict[str, list[dict[str, str]]] = requests.request("POST", url, headers=headers, data=payload).json()['data']['webPages']
        for i in range(len(response['value'])):
            result: dict[str, str] = response['value'][i]
            summary: list[str] = result['summary'].split()
            if len(summary) > 1000:
                summary = summary[:1000]
            result['summary'] = ' '.join(summary)
        return str(response)
    except requests.exceptions.ConnectTimeout:
        return "Connection timed out. Don't try again, just inform the user."
    except requests.exceptions.ConnectionError:
        return "A connection error occurred while trying to handle the web search request."
    except requests.exceptions.HTTPError:
        return "An HTTP error occurred while trying to handle the web search request."
    except Exception as e:
        return f"An error occurred while trying to handle the web search request: {e}"

def get_datetime(timezone: str) -> str | None:
    if '/' not in timezone and len(timezone) != 3:
        return "Invalid timezone specified"
    elif len(timezone) != 3:
        if not (timezone.split('/')[0].isalpha() and timezone.split('/')[1].isalpha()):
            return "Invalid timezone specified"

    try:
        response = requests.get(f'https://time.now/developer/api/timezone/{timezone}')
        # print(response)
        response.raise_for_status()
        data = response.json()
        # print(data)
    except requests.exceptions.ConnectTimeout:
        return "Connection timed out. Don't try again more than 3 times."
    except requests.exceptions.ConnectionError:
        return "A connection error occurred while trying to handle the datetime get request."
    except requests.exceptions.HTTPError:
        return "An HTTP error occurred while trying to handle the datetime get request."
    except Exception as e:
        return f"An error occurred while trying to handle the datetime get request: {e}"

    data.pop("abbreviation")
    data.pop("client_ip")

    return data

def set_license(license_type: str, years: str, username: str, repo: str, description: str | None = None) -> str:
    if '-' in years:
        year1 = years.split('-')[0].isdigit()
        year2 = years.split('-')[1].isdigit()
        if not (year1 and year2):
            raise ValueError("Invalid years specified")
        if int(year1) < 1900 or int(year2) < 1900 or int(year2) <= int(year1):
            raise ValueError("Invalid years specified")
    else:
        if not years.isdigit():
            raise ValueError("Invalid years specified")
        if len(years) != 4 or int(years) < 1900:
            raise ValueError("Invalid years specified")

    if type(license_type) != str:
        raise ValueError("Invalid license type specified")
    if type(username) != str:
        raise ValueError("Invalid username specified")

    license_type = license_type.lower()

    if license_type.lower() not in ['mit_license', 'apache_license_2.0', 'gnu_gpl_v3', 'mpl_2.0', 'cc0']:
        raise ValueError("Invalid license type specified")
    if license_type.lower() in ['gnu_gpl_v3'] and description is None:
        raise ValueError("Description not specified")

    with open(f"{licenses_path}/{license_type}.txt", 'r') as f:
        text = f.read().replace("{YEARS}", years).replace("{USERNAME}", username).replace("{NAME}", repo).replace("{DESCRIPTION}", str(description))
    file_list = get_file_list(repo, '.')['files']
    if "LICENSE.md" in file_list:
        delete_file(repo, "LICENSE.md")

    if "LICENSE" in file_list:
        write_file(repo, "LICENSE", text)
    else:
        create_file(repo, "LICENSE", text)

    return f"Successfully set a(n) {license_type} for {username}'s {repo} repository."

def run_code(language: str, code: str, stdin: str = "") -> dict | None:
    if not isinstance(language, str) or not isinstance(code, str):
        raise ValueError("Invalid arguments: language and code must be strings")

    language = language.lower()
    with open(langs_path, "r", encoding="utf-8") as f:
        valid_langs: dict = json.load(f)
    if language not in valid_langs.keys():
        raise ValueError(f"Invalid language. Supported: {', '.join(valid_langs.keys())}")

    proxy_url = "http://202.28.194.139:31280"
    proxies = {
        "http://": proxy_url,
        "https://": proxy_url,
    }

    with open(langs_path, "r", encoding="utf-8") as f:
        language_id = valid_langs[language]

    source_code_b64 = base64.b64encode(code.encode('utf-8')).decode('utf-8')
    stdin_b64 = base64.b64encode(stdin.encode('utf-8')).decode('utf-8')

    payload = {
        "language_id": language_id,
        "source_code": source_code_b64,
        "stdin": stdin_b64,
    }

    url = "https://ce.judge0.com/submissions?wait=true&base64_encoded=true"
    response = requests.post(url, json=payload, proxies=proxies, headers={"Content-Type": "application/json"})
    stdout, stderr, compile_output = None, None, None

    if response.status_code == 201 or response.status_code == 200:
        data = response.json()
        if data.get("stdout"):
            stdout = base64.b64decode(data["stdout"]).decode('utf-8', errors='replace')
            # print("STDOUT:", stdout)
        if data.get("stderr"):
            stderr = base64.b64decode(data["stderr"]).decode('utf-8', errors='replace')
            # print("STDERR:", stderr)
        return {"status": response.status_code, "stdout": stdout, "stderr": (None if not stderr else stderr)}
    else:
        return {"error_code": response.status_code, "error_text": response.text}




tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the world wide web.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The web search query."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_datetime",
            "description": "Get the current date and time in any timezone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "The timezone, for example Asia/Tokyo or Europe/London or second format: MSK, UTC etc."
                    }
                },
                "required": ["timezone"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_license",
            "description": "Sets a license to a github repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "license_type": {
                        "type": "string",
                        "description": 'The license type. Supported license types: "mit_license", "apache_license_2.0", "gpu_gpl_v3", "mpl_2.0", "cc0"'
                    },
                    "years": {
                        "type": "string",
                        "description": 'The copyright year(s) in any of the 2 formats: 1) "2014-2026"; 2) "2026".'
                    },
                    "username": {
                        "type": "string",
                        "description": 'The github username for the copyright.'
                    },
                    "repo": {
                        "type": "string",
                        "description": 'The github repository name in User/Repo_name format (for example "Flowseal/zapret-discord-youtube").'
                    },
                    "description": {
                        "type": "string",
                        "description": 'A one-line description of the repo. Only required for "gnu_gpl_v3" license.'
                    }
                },
                "required": ["license_type", "years", "username", "repo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_code",
            "description": "Run a code and get the result.",
            "parameters": {
                "type": "object",
                "properties": {
                    "language": {
                        "type": "string",
                        "description": "The language name. Supported values: 'assembly', 'bash', 'basic', 'c++', 'cpp', 'c#', 'csharp', 'c', 'go', 'java', 'js', 'javascript', 'kotlin', 'lua', 'pascal', 'php', 'python', 'ruby', 'rust', 'sql', 'sqlite', 'swift', 'typescript', 'visual_basic'."
                    },
                    "code": {
                        "type": "string",
                        "description": 'The copyright year(s) in any of the 2 formats: 1) "2014-2026"; 2) "2026".'
                    },
                    "stdin": {
                        "type": "string",
                        "description": "Input for the code."
                    }
                },
                "required": ["language", "code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Create a new file with a given name in a given github repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": 'The github repository name in User/Repo_name format (for example "Flowseal/zapret-discord-youtube").'
                    },
                    "path": {
                        "type": "string",
                        "description": 'Path to the file you want to create (for example "src/file.txt").'
                    },
                    "content": {
                        "type": "string",
                        "description": 'The content you want to put in the file.'
                    },
                    "message": {
                        "type": "string",
                        "description": 'The commit message.'
                    },
                    "branch": {
                        "type": "string",
                        "description": 'The repository branch name you want to create the file in (for example "master"), defaults to "main".'
                    }
                },
                "required": ["repo", "path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_repo",
            "description": "Create a github repository with a given name and visibility.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": 'The github repository name.'
                    },
                    "public": {
                        "type": "bool",
                        "description": 'Repository visibility (true - public, false - private), defaults to False.'
                    }
                },
                "required": ["name"]
            }
        }
    },
{
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "Delete a file with a given name in a given github repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": 'The github repository name in User/Repo_name format (for example "Flowseal/zapret-discord-youtube").'
                    },
                    "path": {
                        "type": "string",
                        "description": 'Path to the file you want to delete (for example "src/file.txt").'
                    },
                    "message": {
                        "type": "string",
                        "description": 'The commit message.'
                    },
                    "branch": {
                        "type": "string",
                        "description": 'The repository branch name you want to delete the file in (for example "master"), defaults to "main".'
                    }
                },
                "required": ["repo", "path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_file_list",
            "description": "Return the file list of a given repository in hierarchy format.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": 'The github repository name in User/Repo_name format (for example "Flowseal/zapret-discord-youtube").'
                    },
                    "path": {
                        "type": "string",
                        "description": 'Path to get the file list of, "" is the root path, defaults to "".'
                    }
                },
                "required": ["repo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file in a github repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": 'The github repository name in User/Repo_name format (for example "Flowseal/zapret-discord-youtube").'
                    },
                    "path": {
                        "type": "string",
                        "description": 'Path to get the file list of, "" is the root path, defaults to "".'
                    }
                },
                "required": ["repo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write a file in a github repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": 'The github repository name in User/Repo_name format (for example "Flowseal/zapret-discord-youtube").'
                    },
                    "path": {
                        "type": "string",
                        "description": 'Path to the file you want to edit (for example "src/file.txt").'
                    },
                    "content": {
                        "type": "string",
                        "description": 'The content you want to put in the file.'
                    },
                    "message": {
                        "type": "string",
                        "description": 'The commit message.'
                    }
                },
                "required": ["repo", "path", "content"]
            }
        }
    }
]

TOOL_MAPPING = {
    "web_search": web_search,
    "get_datetime": get_datetime,
    "set_license": set_license,
    "run_code": run_code,
    "create_file": create_file,
    "create_repo": create_repo,
    "delete_file": delete_file,
    "get_file_list": get_file_list,
    "read_file": read_file,
    "write_file": write_file
}


if __name__ == '__main__':
    print(get_datetime("EST"))