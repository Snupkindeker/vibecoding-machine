# Используем официальный образ Python с оптимизацией по размеру
FROM python:3.13-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем системные зависимости (опционально, если потребуются для некоторых пакетов)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     gcc \
#     && apt-get clean && rm -rf /var/lib/apt/lists/*

# Устанавливаем необходимые Python-пакеты
RUN pip install -r requirements.txt

# Копируем все файлы проекта (включая папку ai, palette.py, app.py, terminal.py, run_both.py)
COPY . .

# Открываем порт, на котором работает Streamlit (по умолчанию 8501)
EXPOSE 8501

# Запускаем скрипт, который параллельно запускает Streamlit и терминальный интерфейс
CMD ["python", "run_both.py"]