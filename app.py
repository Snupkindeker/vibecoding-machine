import streamlit as st
import sys
import os
import json
import time

ai_dir = os.path.join(os.path.dirname(__file__), 'ai')
if ai_dir not in sys.path:
    sys.path.append(ai_dir)

from ai.run_cycle import run_cycle
from ai.make_context import make_context
from ai.system_context import system_context
import ai.config as config

# Инициализация
if "messages" not in st.session_state:
    st.session_state.messages = [system_context()]
if "thinking_steps" not in st.session_state:
    st.session_state.thinking_steps = []

# Папка для диалогов
dialogs_dir = os.path.join(ai_dir, 'dialogs')
os.makedirs(dialogs_dir, exist_ok=True)

st.set_page_config(page_title="Vibecoding Machine", layout="wide")
st.title("🤖 Vibecoding Machine")
st.caption("Управляй GitHub через ИИ — с отображением мышления в реальном времени")

# Боковая панель
with st.sidebar:
    st.header("⚙️ Настройки")
    st.write(f"**Модель:** `{config.model_name}`")
    st.write(f"**Лимит операций:** `{config.model_operation_limit}`")
    st.write(f"**GitHub:** `{config.github_username}`")
    st.write(f"**Регистр:** `{config.coding_case}`")
    st.write(f"**Markdown:** `{config.use_markdown}`")
    st.write(f"**Языки:** `{'any' if not config.preferred_languages else ', '.join(config.preferred_languages)}`")

    if st.button("🧹 Очистить историю"):
        st.session_state.messages = [system_context()]
        st.session_state.thinking_steps = []
        st.rerun()

    if st.button("💾 Сохранить диалог"):
        filename = f"dialog_{int(time.time())}.json"
        filepath = os.path.join(dialogs_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(st.session_state.messages, f, ensure_ascii=False, indent=4)
        st.success(f"Диалог сохранён как `{filename}`")
        # Добавляем сообщение в чат
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"✅ Диалог сохранён в `{filename}`"
        })
        st.rerun()

    # Управление файлами диалогов
    files = [f for f in os.listdir(dialogs_dir) if f.endswith('.json')]
    if files:
        st.divider()
        st.subheader("📂 Управление диалогами")
        selected = st.selectbox("Выберите файл", files)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📂 Загрузить"):
                filepath = os.path.join(dialogs_dir, selected)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        loaded = json.load(f)
                    if isinstance(loaded, list) and all(isinstance(m, dict) for m in loaded):
                        st.session_state.messages = loaded
                        st.session_state.thinking_steps = []
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"✅ Загружен диалог из `{selected}`"
                        })
                        st.rerun()
                    else:
                        st.error("Неверный формат файла")
                except Exception as e:
                    st.error(f"Ошибка загрузки: {e}")
        with col2:
            if st.button("🗑️ Удалить"):
                filepath = os.path.join(dialogs_dir, selected)
                try:
                    os.remove(filepath)
                    st.success(f"Файл `{selected}` удалён")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"✅ Файл `{selected}` удалён."
                    })
                    # Обновляем список файлов, убираем удалённый
                    st.rerun()
                except Exception as e:
                    st.error(f"Ошибка удаления: {e}")
    else:
        st.info("Нет сохранённых диалогов")

    st.divider()
    st.caption("💡 Команды: /help, /wipe, /config, /save, /load, /del")

# Отображение истории сообщений
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.write(msg["content"])
    elif msg["role"] == "tool":
        with st.expander("🛠️ Вызов инструмента"):
            try:
                st.json(json.loads(msg["content"]))
            except:
                st.write(msg["content"])

# Отображение сохранённого мышления
if st.session_state.thinking_steps:
    with st.expander("🧠 Мышление модели (шаги)", expanded=False):
        for step in st.session_state.thinking_steps:
            st.write(step)


# Функция обработки команд
def handle_command(command: str) -> str | None:
    args = command.split()
    cmd = args[0].lower()

    if cmd == "/help":
        return (
            "**Доступные команды:**\n"
            "- `/help` – показать это меню\n"
            "- `/wipe` – очистить историю диалога\n"
            "- `/config` – показать текущие настройки\n"
            "- `/config <параметр> <значение>` – изменить параметр\n"
            "- `/config check` – проверить конфиг на ошибки\n"
            "- `/config reset` – сбросить конфиг к значениям по умолчанию\n"
            "- `/save <имя>` – сохранить текущий диалог (без расширения)\n"
            "- `/load <имя>` – загрузить диалог из файла\n"
            "- `/del <имя>` – удалить файл диалога"
        )
    elif cmd == "/wipe":
        st.session_state.messages = [system_context()]
        st.session_state.thinking_steps = []
        return "🗑️ История диалога очищена."
    elif cmd == "/config":
        if len(args) == 1:
            return (
                f"**Текущие настройки:**\n"
                f"- model_name: `{config.model_name}`\n"
                f"- model_operation_limit: `{config.model_operation_limit}`\n"
                f"- github_username: `{config.github_username}`\n"
                f"- coding_case: `{config.coding_case}`\n"
                f"- use_markdown: `{config.use_markdown}`\n"
                f"- preferred_languages: `{'any' if not config.preferred_languages else ', '.join(config.preferred_languages)}`"
            )
        elif len(args) == 2 and args[1] == "check":
            try:
                config.check_config()
                return "✅ Конфиг проверен, ошибок нет."
            except config.ConfigError as e:
                return f"❌ Ошибка в конфиге: {e}"
        elif len(args) == 2 and args[1] == "reset":
            config.set_default_config()
            return "✅ Конфиг сброшен к значениям по умолчанию."
        elif len(args) == 3:
            key, value = args[1], args[2]
            if key == "model_name":
                config.model_name = value
                return f"✅ model_name установлен в `{value}`"
            elif key == "model_operation_limit":
                try:
                    config.model_operation_limit = int(value)
                    return f"✅ model_operation_limit установлен в `{value}`"
                except ValueError:
                    return "❌ Ошибка: значение должно быть целым числом"
            elif key == "github_username":
                config.github_username = value
                return f"✅ github_username установлен в `{value}`"
            elif key == "coding_case":
                if value in ['snake', 'camel', 'pascal']:
                    config.coding_case = value
                    return f"✅ coding_case установлен в `{value}`"
                else:
                    return "❌ Ошибка: допустимы snake, camel, pascal"
            elif key == "use_markdown":
                if value.lower() in ['true', 'false']:
                    config.use_markdown = value.lower() == 'true'
                    return f"✅ use_markdown установлен в `{config.use_markdown}`"
                else:
                    return "❌ Ошибка: допустимы true/false"
            elif key == "preferred_languages":
                if value == "any":
                    config.preferred_languages = []
                    return "✅ preferred_languages установлен в `any`"
                else:
                    langs = [lang.strip() for lang in value.split(',')]
                    config.preferred_languages = langs
                    return f"✅ preferred_languages установлен в `{', '.join(langs)}`"
            else:
                return f"❌ Неизвестный параметр: `{key}`"
        else:
            return "❌ Неверный формат. Используйте: `/config`, `/config check`, `/config reset` или `/config <параметр> <значение>`"
    elif cmd == "/save":
        if len(args) != 2:
            return "❌ Использование: `/save <имя_файла_без_расширения>`"
        filename = args[1].strip() + ".json"
        filepath = os.path.join(dialogs_dir, filename)
        if os.path.exists(filepath):
            return f"❌ Файл `{filename}` уже существует. Используйте другое имя."
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(st.session_state.messages, f, ensure_ascii=False, indent=4)
            return f"✅ Диалог сохранён в `{filename}`"
        except Exception as e:
            return f"❌ Ошибка сохранения: {e}"
    elif cmd == "/load":
        if len(args) != 2:
            return "❌ Использование: `/load <имя_файла_без_расширения>`"
        filename = args[1].strip() + ".json"
        filepath = os.path.join(dialogs_dir, filename)
        if not os.path.exists(filepath):
            return f"❌ Файл `{filename}` не найден."
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            if isinstance(loaded, list) and all(isinstance(m, dict) for m in loaded):
                st.session_state.messages = loaded
                st.session_state.thinking_steps = []
                return f"✅ Диалог загружен из `{filename}`"
            else:
                return "❌ Неверный формат файла"
        except Exception as e:
            return f"❌ Ошибка загрузки: {e}"
    elif cmd == "/del":
        if len(args) != 2:
            return "❌ Использование: `/del <имя_файла_без_расширения>`"
        filename = args[1].strip() + ".json"
        filepath = os.path.join(dialogs_dir, filename)
        if not os.path.exists(filepath):
            return f"❌ Файл `{filename}` не найден."
        try:
            os.remove(filepath)
            return f"✅ Файл `{filename}` удалён."
        except Exception as e:
            return f"❌ Ошибка удаления: {e}"
    else:
        return f"❌ Неизвестная команда: `{cmd}`. Используйте /help."


# Поле ввода
if prompt := st.chat_input("Напишите сообщение или команду (начинается с /)..."):
    if prompt.startswith('/'):
        result = handle_command(prompt)
        if result:
            st.session_state.messages.append({"role": "assistant", "content": result})
        st.rerun()
    else:
        user_msg = make_context("user", prompt)
        st.session_state.messages.append(user_msg)
        st.session_state.thinking_steps = []

        with st.status("🧠 Мышление модели...", expanded=True) as status:
            for event in run_cycle(st.session_state.messages):
                if event['type'] == 'llm_call':
                    msg = "🤖 Модель анализирует запрос..."
                    status.write(msg)
                    st.session_state.thinking_steps.append(msg)
                elif event['type'] == 'tool_call':
                    args_str = json.dumps(event['data']['arguments'], ensure_ascii=False)
                    msg = f"🔧 Вызов `{event['data']['name']}` с аргументами: `{args_str}`"
                    status.write(msg)
                    st.session_state.thinking_steps.append(msg)
                elif event['type'] == 'tool_result':
                    result_preview = json.dumps(event['data']['result'], ensure_ascii=False)[:200]
                    msg = f"✅ Результат `{event['data']['name']}`: `{result_preview}...`"
                    status.write(msg)
                    st.session_state.thinking_steps.append(msg)
                elif event['type'] == 'final_answer':
                    msg = f"💬 Ответ: {event['data']['content'][:500]}..."
                    status.write(msg)
                    st.session_state.thinking_steps.append(msg)
                    if st.session_state.messages[-1]["role"] != "assistant":
                        st.session_state.messages.append(make_context("assistant", event['data']['content']))
                elif event['type'] == 'warning':
                    msg = f"⚠️ {event['data']['message']}"
                    status.write(msg)
                    st.session_state.thinking_steps.append(msg)

            status.update(label="✅ Готово!", state="complete")

        st.rerun()