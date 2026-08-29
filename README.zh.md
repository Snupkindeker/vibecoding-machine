# 🤖 vibecoding-machine

**vibecoding-machine** 是一个由人工智能驱动的编程助手，它将大语言模型（LLM）与用于 GitHub 开发的真实工具连接起来。你可以在终端或现代 Web 界面（Streamlit）中与它聊天，它会为你规划并执行多步骤任务：创建仓库、管理文件、设置许可证、搜索网页，以及在 20+ 种编程语言中运行代码。

该助手会根据你的偏好（代码风格、是否使用 Markdown、偏好的编程语言）构建自己的行为，遵守安全规则，并向你展示它所执行的每一步。

[**English**](README.md) | [**Русский**](README.ru.md) | [**Español**](README.es.md) | [**中文**](README.zh.md)

## ✨ 特性

- 🧠 **基于 LLM 的智能体** — 使用函数调用（function calling）根据单条指令规划并完成多步骤任务。
- 💬 **双界面** — 彩色终端聊天（`terminal.py`）和基于 Streamlit 的现代浏览器界面（`app.py`）。
- 🔧 **GitHub 工具** — 创建仓库、读取/写入/删除文件、列出仓库内容。
- 📜 **许可证管理器** — 自动设置 MIT、Apache-2.0、GPL-3.0、MPL-2.0 或 CC0 许可证。
- 🌐 **网页搜索** — 通过 Langsearch API 内置的搜索功能。
- 🕒 **日期时间工具** — 获取任意时区的当前日期和时间。
- 🧪 **代码运行器** — 在 20+ 种语言中执行代码（基于 Judge0），支持 stdout/stderr 输出。
- ⚙️ **运行时配置** — 通过 `/config` 即时更改模型、操作次数上限、偏好和语言。
- 🌍 **多语言界面** — 支持 13 种界面语言。
- 🐳 **Docker 支持** — 提供容器镜像和自动发布工作流。

## 🛠️ 工作原理

1. 你从终端或 Web 界面发送一条消息。
2. 助手根据 `ai/config.py` 中的偏好生成系统提示词，并调用 LLM。
3. 如果模型决定调用某个工具，则执行该工具并将结果返回给模型。
4. 循环重复进行，直到模型给出最终答案（最多 `model_operation_limit` 次迭代）。

## 📦 环境要求

- Python 3.10+（推荐 3.13；仓库的 `python/` 目录中内置了 Windows 便携版 Python）
- 兼容 OpenAI 的 LLM API 密钥和端点
- 用于网页搜索的 Langsearch API 密钥（可选，但建议配置）

## 🔧 安装

```bash
# 1. 克隆仓库
git clone https://github.com/Snupkindeker/vibecoding-machine.git
cd vibecoding-machine

# 2. 创建并激活虚拟环境（推荐）
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 创建包含密钥的 .env 文件
AI_API_KEY=your_llm_api_key
AI_API_ENDPOINT=https://your-llm-endpoint/v1
LANGSEARCH_KEY=your_langsearch_api_key
```

在 Windows 上，还可以使用现成的启动脚本：`run.bat`、`run.ps1` 或 `start_app.bat`。

## ⚙️ 配置

主要设置位于 [`ai/config.py`](ai/config.py)：

| 设置项 | 说明 | 默认值 |
| --- | --- | --- |
| `model_name` | 聊天所使用的 LLM 模型 | `deepseek-v4-flash-0731` |
| `model_operation_limit` | 每条指令最多允许的工具调用 + 推理步骤数 | `25` |
| `github_username` | 你的 GitHub 用户名（GitHub 工具必需） | `Snupkindeker` |
| `coding_case` | `snake`、`camel` 或 `pascal` | `snake` |
| `use_markdown` | AI 是否应使用 Markdown | `True` |
| `preferred_languages` | 偏好的编程语言（留空 = 任意语言） | `[]` |
| `language` | 界面语言：`en`、`ru`、`es` 等 | `en` |

## 🚀 使用方法

### 💻 终端界面

```bash
python terminal.py
```

### 🌐 Web 界面（Streamlit）

```bash
streamlit run app.py
```

### 🚀 同时启动两者

```bash
python main.py
```

该命令会在后台启动 Streamlit 应用，并在当前终端运行终端聊天。按 `Ctrl+C` 或输入 `/stop` 即可退出。

## ⌨️ 命令

| 命令 | 说明 |
| --- | --- |
| `/help` | 显示帮助信息 |
| `/stop` | 退出聊天 |
| `/wipe` | 清空对话历史 |
| `/config` | 显示当前配置 |
| `/config check` | 校验配置 |
| `/config reset` | 将配置重置为默认值 |
| `/config <键> <值>` | 更改单个设置项 |
| `/save <名称>` | 保存当前对话 |
| `/load <名称>` | 加载已保存的对话 |
| `/del <名称>` | 删除已保存的对话 |

已保存的对话以 JSON 格式存储在 `ai/dialogs/` 目录中。

## 🧰 AI 工具

| 工具 | 说明 |
| --- | --- |
| `web_search` | 搜索网页 |
| `get_datetime` | 获取任意时区的当前日期和时间 |
| `create_repo` | 创建 GitHub 仓库（默认为私有） |
| `set_license` | 设置许可证：MIT、Apache-2.0、GPL-3.0、MPL-2.0、CC0 |
| `create_file` | 在仓库中创建文件 |
| `write_file` | 编辑仓库中的文件 |
| `read_file` | 读取仓库中的文件 |
| `delete_file` | 删除仓库中的文件 |
| `get_file_list` | 列出仓库内容 |
| `run_code` | 在 20+ 种语言中运行代码（stdin/stdout/stderr） |

## 🌍 本地化

界面支持 **13 种语言**（`locales/*.json`）：英语、俄语、西班牙语、法语、中文、阿拉伯语、德语、韩语、葡萄牙语、日语、印地语、孟加拉语和意大利语。

使用 `/config language <代码>` 命令或 Web 应用的侧边栏即可切换语言。

## 🐳 Docker

仓库包含基于 `python:3.13-slim` 的 [`Dockerfile`](Dockerfile)，`.github/workflows/docker-publish.yml` 会自动发布镜像。

```bash
docker build -t vibecoding-machine .
docker run -p 8501:8501 --env-file .env vibecoding-machine
```

如果只想在容器中运行 Web 界面，请覆盖命令：

```bash
docker run -p 8501:8501 --env-file .env vibecoding-machine streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## 📁 项目结构

```
.
├── ai/                  # AI 核心：配置、工具、运行循环、本地化、对话
├── github_tools/        # GitHub API 封装
├── licenses/            # 许可证模板
├── locales/             # 界面翻译（13 种语言）
├── exceptions/          # 自定义异常
├── python/              # Windows 便携版 Python 3.13
├── app.py               # Streamlit Web 界面
├── terminal.py          # 终端界面
├── main.py              # 同时启动 Web 界面和终端
├── palette.py           # 终端颜色
├── logger_setup.py      # 日志配置
├── requirements.txt     # Python 依赖
├── Dockerfile           # 容器镜像
├── run.bat / run.ps1    # Windows 启动脚本
└── start_app.bat        # Streamlit 启动脚本（Windows）
```

## 📄 许可证

本项目基于 [MIT 许可证](LICENSE) 分发。Copyright © 2026 Snupkindeker。