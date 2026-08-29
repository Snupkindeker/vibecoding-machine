# 🤖 vibecoding-machine

**vibecoding-machine** is an AI-powered coding assistant that connects a large language model (LLM) with real tools for working on GitHub. Chat with it in your terminal or in a modern web interface (Streamlit), and it will plan and execute multi-step tasks for you: creating repositories, managing files, setting licenses, searching the web, and running code in 20+ programming languages.

The assistant builds its behavior from your preferences (coding case, Markdown usage, preferred languages), follows safety rules and shows you every step it takes.

[**English**](README.md) | [**Русский**](README.ru.md) | [**Español**](README.es.md) | [**中文**](README.zh.md)

## ✨ Features

- 🧠 **LLM-powered agent** — uses function calling to plan and complete multi-step tasks from a single prompt.
- 💬 **Two interfaces** — a colorful terminal chat (`terminal.py`) and a modern browser UI (`app.py`, built with Streamlit).
- 🔧 **GitHub tools** — create repositories, read/write/delete files, list repository contents.
- 📜 **License manager** — set MIT, Apache-2.0, GPL-3.0, MPL-2.0 or CC0 licenses automatically.
- 🌐 **Web search** — built-in search via the Langsearch API.
- 🕒 **Datetime tool** — get the current date and time in any timezone.
- 🧪 **Code runner** — execute code in 20+ languages (Judge0 backend) with stdout/stderr output.
- ⚙️ **Runtime configuration** — change the model, operation limits, preferences and language on the fly with `/config`.
- 🌍 **Localized UI** — 13 interface languages.
- 🐳 **Docker support** — container image plus an automatic publish workflow.

## 🛠️ How it works

1. You send a message from the terminal or the web UI.
2. The assistant calls the LLM with a system prompt generated from your `ai/config.py` preferences.
3. If the model decides to call a tool, the tool is executed and its result is returned to the model.
4. The loop repeats until the model produces a final answer (up to `model_operation_limit` iterations).

## 📦 Requirements

- Python 3.10+ (3.13 recommended; a portable Python for Windows is bundled in `python/`)
- An OpenAI-compatible LLM API key and endpoint
- A Langsearch API key for web search (optional but recommended)

## 🔧 Installation

```bash
# 1. Clone the repository
git clone https://github.com/Snupkindeker/vibecoding-machine.git
cd vibecoding-machine

# 2. Create and activate a virtual environment (recommended)
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create a .env file with your keys
AI_API_KEY=your_llm_api_key
AI_API_ENDPOINT=https://your-llm-endpoint/v1
LANGSEARCH_KEY=your_langsearch_api_key
```

On Windows you can also use the ready-made launchers: `run.bat`, `run.ps1` or `start_app.bat`.

## ⚙️ Configuration

Main settings live in [`ai/config.py`](ai/config.py):

| Setting | Description | Default |
| --- | --- | --- |
| `model_name` | The LLM model used for the chat | `deepseek-v4-flash-0731` |
| `model_operation_limit` | Max tool calls + reasoning steps per prompt | `25` |
| `github_username` | Your GitHub username (required for GitHub tools) | `Snupkindeker` |
| `coding_case` | `snake`, `camel` or `pascal` | `snake` |
| `use_markdown` | Whether the AI should use Markdown | `True` |
| `preferred_languages` | Preferred programming languages (empty = any) | `[]` |
| `language` | Interface language: `en`, `ru`, `es`, ... | `en` |

## 🚀 Usage

### 💻 Terminal interface

```bash
python terminal.py
```

### 🌐 Web interface (Streamlit)

```bash
streamlit run app.py
```

### 🚀 Both at once

```bash
python main.py
```

This launches the Streamlit app in the background and the terminal chat in the foreground. Press `Ctrl+C` or type `/stop` to exit.

## ⌨️ Commands

| Command | Description |
| --- | --- |
| `/help` | Show the help message |
| `/stop` | Exit the chat |
| `/wipe` | Clear conversation history |
| `/config` | Show the current configuration |
| `/config check` | Validate the configuration |
| `/config reset` | Reset configuration to defaults |
| `/config <key> <value>` | Change a single setting |
| `/save <name>` | Save the current conversation |
| `/load <name>` | Load a saved conversation |
| `/del <name>` | Delete a saved conversation |

Saved conversations are stored as JSON in `ai/dialogs/`.

## 🧰 AI tools

| Tool | Description |
| --- | --- |
| `web_search` | Search the web |
| `get_datetime` | Get the current date and time in any timezone |
| `create_repo` | Create a GitHub repository (private by default) |
| `set_license` | Set a license: MIT, Apache-2.0, GPL-3.0, MPL-2.0, CC0 |
| `create_file` | Create a file in a repository |
| `write_file` | Edit a file in a repository |
| `read_file` | Read a file from a repository |
| `delete_file` | Delete a file from a repository |
| `get_file_list` | List repository contents |
| `run_code` | Run code in 20+ languages (stdin/stdout/stderr) |

## 🌍 Localization

The interface is available in **13 languages** (`locales/*.json`): English, Russian, Spanish, French, Chinese, Arabic, German, Korean, Portuguese, Japanese, Hindi, Bengali and Italian.

Switch the language with `/config language <code>` or from the sidebar of the web app.

## 🐳 Docker

A [`Dockerfile`](Dockerfile) based on `python:3.13-slim` is included, and `.github/workflows/docker-publish.yml` publishes the image automatically.

```bash
docker build -t vibecoding-machine .
docker run -p 8501:8501 --env-file .env vibecoding-machine
```

To run only the web UI inside a container, override the command:

```bash
docker run -p 8501:8501 --env-file .env vibecoding-machine streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## 📁 Project structure

```
.
├── ai/                  # AI core: config, tools, run cycle, localization, dialogs
├── github_tools/        # GitHub API wrappers
├── licenses/            # License templates
├── locales/             # UI translations (13 languages)
├── exceptions/          # Custom exceptions
├── python/              # Portable Python 3.13 (Windows)
├── app.py               # Streamlit web interface
├── terminal.py          # Terminal interface
├── main.py              # Launches web + terminal together
├── palette.py           # Terminal colors
├── logger_setup.py      # Logging configuration
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container image
├── run.bat / run.ps1    # Windows launchers
└── start_app.bat        # Streamlit launcher (Windows)
```

## 📄 License

Distributed under the [MIT License](LICENSE). Copyright © 2026 Snupkindeker.