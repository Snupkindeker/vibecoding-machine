import json
import requests

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
        response = requests.get('https://time.now/developer/api/timezone/Asia/Tokyo')
        response.raise_for_status()
        data = response.json()
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
                "required": ["repo", "path", "content"]
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
    "create_file": create_file,
    "create_repo": create_repo,
    "delete_file": delete_file,
    "get_file_list": get_file_list,
    "read_file": read_file,
    "write_file": write_file
}


if __name__ == '__main__':
    print(get_datetime('MSK'))