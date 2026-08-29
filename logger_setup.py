import logging
import os
import sys
from logging.handlers import RotatingFileHandler

def setup_logging(log_to_console=False, log_file_name="log.log"):
    """
    Настраивает логирование в файл с ротацией.
    """
    # Определяем базовую папку: сначала пытаемся взять папку, где лежит main.py,
    # если нет – текущую рабочую.
    try:
        # Если приложение собрано PyInstaller, используем sys._MEIPASS
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        # Но в портативной версии лучше взять текущую рабочую папку
        base_dir = os.getcwd()
    except Exception:
        base_dir = os.getcwd()

    logs_dir = os.path.join(base_dir, 'logs')
    try:
        os.makedirs(logs_dir, exist_ok=True)
    except Exception as e:
        # print(f"Не удалось создать папку {logs_dir}: {e}")
        # Попробуем использовать текущую папку
        logs_dir = os.getcwd()

    log_file_path = os.path.join(logs_dir, log_file_name)
    # print(f"Логи будут писаться в: {log_file_path}")  # отладка

    # Очищаем существующие обработчики корневого логгера
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    root_logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    try:
        file_handler = RotatingFileHandler(
            log_file_path, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        # print(f"Обработчик файла добавлен: {log_file_path}")
    except Exception as e:
        print(f"Error while creating file processor: {e}")

    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # Подавляем шум от библиотек
    for lib in ['httpx', 'openai', 'urllib3']:
        logging.getLogger(lib).setLevel(logging.WARNING)

    # Тестовое сообщение
    logging.info("Logging setup successfully!")

# Если нужно, можно сразу вызвать setup_logging() при импорте, но лучше вызывать в main