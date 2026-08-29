# 🤝 Contributing to vibecoding-machine

First of all — thank you for taking the time to contribute! 🎉

**vibecoding-machine** is an AI-powered coding assistant that connects a large language model with real tools for working on GitHub. Whether you are fixing a bug, adding a new tool, improving localization, or polishing the docs — your help is appreciated.

This guide explains how to set up the project, what conventions we follow, and how to get your changes merged smoothly.

---

## 📑 Table of contents

- [Code of conduct](#-code-of-conduct)
- [Reporting issues](#-reporting-issues)
- [Setting up the development environment](#-setting-up-the-development-environment)
- [Project structure](#-project-structure)
- [Running the project](#-running-the-project)
- [Running tests](#-running-tests)
- [Code style & conventions](#-code-style--conventions)
- [Adding a new AI tool](#-adding-a-new-ai-tool)
- [Contributing translations](#-contributing-translations)
- [Branching & git workflow](#-branching--git-workflow)
- [Commit message guidelines](#-commit-message-guidelines)
- [Pull request process](#-pull-request-process)
- [License](#-license)

---

## 🤝 Code of conduct

Be respectful and constructive in all interactions — issues, pull requests, and reviews.

- Be welcoming to newcomers and patient with questions.
- Give concrete, actionable feedback instead of vague criticism.
- Do not insult, harass, or dismiss other contributors.
- Assume good faith: most disagreements come from different contexts, not malice.

Harassment and offensive behavior are not tolerated. Maintainers may close threads or block accounts that violate these rules.

---

## 🐛 Reporting issues

Before opening a new issue:

1. **Search existing issues** — your problem may already be known or fixed.
2. **Check the configuration** — many problems are caused by a missing or wrong `.env` entry or a bad value in `ai/config.py`. Run `/config check` in the chat or call `check_config()` to validate it.
3. **Check the logs** — the project uses `logger_setup.py`; include relevant log lines in your report.

When opening an issue, please include:

- **Describe the bug or feature** — what did you expect, and what actually happened?
- **Steps to reproduce** — the exact prompt or command you used.
- **Environment** — OS, Python version (check with `python --version`), the LLM model/endpoint you use, and whether you run from terminal, Streamlit, or Docker.
- **Relevant code/config snippets** (minus any secrets).

> ⚠️ Never paste API keys, tokens, or other secrets into issues, PRs, or logs.

---

## 🔧 Setting up the development environment

### Prerequisites

- **Python 3.10+** (3.13 recommended — matches CI and the bundled portable Python in `python/`)
- **Git**
- Optional: Docker (for container work), `pip`/`venv`

### 1. Fork & clone

```bash
git clone https://github.com/Snupkindeker/vibecoding-machine.git
cd vibecoding-machine
git remote add upstream https://github.com/Snupkindeker/vibecoding-machine.git
```

> When you are ready to open a PR, work from your own fork.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows (cmd)
.venv\Scripts\activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Linux/macOS
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the `.env` file

```bash
AI_API_KEY=your_llm_api_key
AI_API_ENDPOINT=https://your-llm-endpoint/v1
LANGSEARCH_KEY=your_langsearch_api_key   # optional but recommended
```

`.env` is git-ignored; never commit it. Add a `python-dotenv`-compatible `.env.example` in the repo root if you want to document new variables.

### 5. Sanity check

```bash
python -c "from ai.config import check_config; check_config(); print('config OK')"
```

---

## 📁 Project structure

```
.
├── ai/                  # AI core: config, tools, run cycle, system context, localization, dialogs
├── github_tools/        # GitHub API wrappers (create/read/write/delete files, repos, licenses)
├── licenses/            # License templates (MIT, Apache-2.0, GPL-3.0, MPL-2.0, CC0)
├── locales/             # UI translations (13 languages, JSON)
├── exceptions/          # Custom exceptions (e.g. ConfigError)
├── tests/               # pytest test suite
├── python/              # Portable Python 3.13 (Windows, do not modify)
├── app.py               # Streamlit web interface
├── terminal.py          # Terminal chat interface
├── main.py              # Launches web + terminal together
├── palette.py           # Terminal colors
├── logger_setup.py      # Logging configuration
└── requirements.txt     # Python dependencies
```

---

## 🚀 Running the project

| Interface | Command |
| --- | --- |
| Terminal chat | `python terminal.py` |
| Web UI (Streamlit) | `streamlit run app.py` |
| Both at once | `python main.py` |

Windows launchers are also available: `run.bat`, `run.ps1`, `start_app.bat`.

Useful in-chat commands for development:

| Command | Purpose |
| --- | --- |
| `/config` | Show current configuration |
| `/config check` | Validate configuration |
| `/config reset` | Reset to defaults |
| `/config <key> <value>` | Change a setting on the fly |
| `/wipe` | Clear conversation history |
| `/save`, `/load`, `/del` | Manage saved conversations (`ai/dialogs/`) |

---

## 🧪 Running tests

The test suite lives in `tests/` and uses **pytest**. CI runs it on Python 3.13 with:

```bash
pytest tests/ -v --tb=short
```

Run it locally **before** pushing — make sure everything passes and no new tests are skipped silently.

### Test conventions

- Test files mirror modules: `test_context.py`, `test_tools.py`, `test_run_cycle.py`, `test_github_tools.py`.
- Test functions start with `test_` and are plain functions (no classes required).
- Modules that live outside `tests/` are imported with an explicit `sys.path` insert — keep this pattern for consistency:

  ```python
  import sys
  import os

  sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

  from ai.make_context import make_context
  ```

- Prefer simple, descriptive asserts over mocking frameworks where possible.

> 💡 The CI workflow (`run_tests.yml`) runs on `push` to `main`/`develop`, on PRs to `main`, and on releases — so a red pipeline will block your merge.

---

## 🎨 Code style & conventions

We keep the code clean, readable, and consistent:

- **Naming:** `snake_case` for variables, functions, and file names; `UPPER_SNAKE_CASE` for constants. This matches the project's `coding_case` default.
- **Type hints:** annotate function signatures and public variables (`list[str]`, `dict[str, str]`, etc.).
- **Docstrings:** add short docstrings to functions with non-obvious behavior (see `ai/run_cycle.py` for the generator-event style).
- **Section comments:** use `# ------ Section name -------` separators to group related code blocks (see `ai/config.py`).
- **Formatting:** keep lines reasonably short, 4-space indentation, no trailing whitespace.
- **Imports:** standard library first, then third-party, then local modules.
- **Logging:** use the `logger` from `logger_setup.py` instead of `print()` for diagnostics.
- **No secrets:** never hardcode API keys, proxy URLs, or personal usernames. These belong in `.env` / `ai/config.py` only.

Run `/config check` before committing if your change touches configuration.

---

## 🔧 Adding a new AI tool

AI tools are defined in `ai/tools.py` and dispatched through the `TOOL_MAPPING` dict. To add one:

1. Implement a function for your tool (pure logic, no secrets inside).
2. Register it in `TOOL_MAPPING` so the run cycle can call it.
3. Add a `locales/` entry (the key the UI uses to describe the tool).
4. Add tests to `tests/test_tools.py` covering happy path and edge cases.
5. Update the tool table in `README.md` if the feature is user-visible.
6. Run `pytest tests/ -v` and verify the full loop works in `terminal.py`.

Tools must follow the system restrictions described in `ai/system_context.py` (no illegal/inappropriate software, private repos by default, no destructive actions without permission).

---

## 🌍 Contributing translations

The UI is localized in **13 languages** (`locales/*.json`): `ar, bn, de, en, es, fr, hi, it, ja, ko, pt, ru, zh`.

To add or fix a translation:

1. Copy `locales/en.json` as the base and translate the values — **do not rename or remove keys**.
2. Save the file as `locales/<code>.json` using the [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) language code.
3. Register the new language code in `ai/localization.py` and, if needed, in `ai/config.py` comments.
4. If the main README is translated, add the language to the README language switcher.

Keep translations natural and consistent with existing tone. Machine-translated bulk PRs are usually fine for missing keys but should be reviewed by a native speaker.

---

## 🌿 Branching & git workflow

The project uses two main branches:

- **`main`** — stable, always deployable. Receives code via PRs only.
- **`develop`** — integration branch where ongoing work is merged first.

Workflow:

1. Create a feature branch from `develop` (or `main` for hotfixes):

   ```bash
   git checkout develop
   git pull upstream develop
   git checkout -b feature/my-awesome-feature
   ```

2. Make focused commits (see [commit guidelines](#-commit-message-guidelines)).
3. Keep your branch up to date with `develop`.
4. Open a pull request **into `develop`** (hotfixes may target `main` directly).

---

## ✍️ Commit message guidelines

Write clear, imperative, single-line commit messages starting with a capitalized verb:

```
Add validation for the run_cycle limit
Fix crash when dialogs folder is missing
Update ru.json with missing localization keys
Refactor tool dispatch into TOOL_MAPPING
```

Optionally prefix with the conventional commit type: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.

Guidelines:

- Keep the first line under ~72 characters.
- Describe **why**, not just what, in the body when it matters.
- One logical change per commit; avoid bundling unrelated edits.
- Do not commit `.env`, secrets, virtual environments, `.pytest_cache`, or `python/` binaries.

---

## 🔀 Pull request process

1. **Open early, mark as draft** if the work is in progress — visibility helps avoid duplicate effort.
2. Fill in the PR template: what changed, why, how it was tested, any screenshots/logs.
3. Make sure CI is green: `pytest tests/ -v --tb=short` must pass.
4. Add a `Closes #<issue>` line when the PR fixes an issue.
5. Request review; respond to feedback with new commits (no force-pushing unless necessary).
6. Once approved, the maintainer merges your PR. If you merge yourself, prefer **squash merge** for small/medium changes.

**Review checklist for reviewers:**

- [ ] Code follows the style guide (snake_case, type hints, docstrings)
- [ ] Tests are added/updated and pass locally
- [ ] No secrets or environment-specific values are hardcoded
- [ ] Localization keys are consistent (no missing/renamed keys)
- [ ] Docs (`README*.md`) updated if user-facing behavior changed

---

## 📄 License

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE), © Snupkindeker.

---

Again — thank you for contributing! If you have questions, open an issue and we will help you get started. 💙