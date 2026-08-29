import logging
import os
import sys
from logging.handlers import RotatingFileHandler


def setup_logging(log_to_console=False, log_file_name="vibecoding.log"):
    """
    Настраивает логирование в файл с ротацией и, опционально, в консоль.

    Аргументы:
        log_to_console (bool): если True, логи также выводятся в консоль.
        log_file_name (str): имя файла для логов (будет лежать в папке logs/).
    """
    # Определяем корневую папку проекта (там, где лежит этот скрипт)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logs_dir = os.path.join(base_dir, 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    log_file_path = os.path.join(logs_dir, log_file_name)

    # Создаём корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Удаляем все существующие обработчики (чтобы избежать дублирования)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Формат логов
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Обработчик для файла (с ротацией, макс. размер 5 МБ, храним 3 файла)
    file_handler = RotatingFileHandler(
        log_file_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Если нужен вывод в консоль (например, для отладки)
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # Подавляем лишние логи от некоторых библиотек (опционально)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)