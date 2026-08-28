#!/usr/bin/env python3
"""
run_both.py – Запуск Streamlit-приложения и терминального клиента параллельно.
Streamlit работает в фоновом процессе, terminal – в текущем терминале с доступом к вводу.
Завершение по Ctrl+C или при остановке terminal (команда /stop).
"""

import subprocess
import sys
import os
import signal
import time

def main():
    # Определяем базовую директорию (там, где лежит этот скрипт)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Пути к запускаемым файлам
    app_path = os.path.join(base_dir, 'app.py')
    terminal_path = os.path.join(base_dir, 'terminal.py')

    # Проверяем существование файлов
    if not os.path.isfile(app_path):
        print(f"Error: {app_path} file not found.")
        sys.exit(1)
    if not os.path.isfile(terminal_path):
        print(f"Error: {terminal_path} file not found.")
        sys.exit(1)

    # Запускаем Streamlit через модуль streamlit (используем тот же интерпретатор)
    # Опция --server.headless=true подавляет автоматическое открытие браузера
    streamlit_cmd = [
        sys.executable, '-m', 'streamlit', 'run', app_path,
        '--server.headless', 'true'
    ]
    # Запускаем в фоне, stdout/stderr перенаправляем в текущий терминал (не перехватываем)
    proc_streamlit = subprocess.Popen(streamlit_cmd, stdout=None, stderr=None)

    print(f"Streamlit started (PID: {proc_streamlit.pid}).")
    print("Starting terminal interface. Type /stop or press Ctrl+C to exit.\n")

    # Запускаем terminal.py – он будет использовать тот же stdin/stdout/stderr,
    # что и родительский процесс, т.е. мы сможем вводить команды.
    proc_terminal = subprocess.Popen([sys.executable, terminal_path])

    # Обработчик сигнала для корректного завершения дочерних процессов
    def terminate_children(*args):
        print("\nEnding processes...")
        proc_streamlit.terminate()
        proc_terminal.terminate()
        # Даём время на корректное завершение
        for _ in range(5):
            if proc_streamlit.poll() is not None and proc_terminal.poll() is not None:
                break
            time.sleep(0.5)
        # Принудительно убиваем, если не завершились
        if proc_streamlit.poll() is None:
            proc_streamlit.kill()
        if proc_terminal.poll() is None:
            proc_terminal.kill()
        sys.exit(0)

    # Перехватываем SIGINT (Ctrl+C) и SIGTERM
    signal.signal(signal.SIGINT, terminate_children)
    signal.signal(signal.SIGTERM, terminate_children)

    # Ждём завершения терминального процесса (он может завершиться по команде /stop)
    try:
        proc_terminal.wait()
    except KeyboardInterrupt:
        terminate_children()

    # Если terminal завершился, завершаем и streamlit
    if proc_streamlit.poll() is None:
        print("\nTerminal process ended, stopping Streamlit...")
        proc_streamlit.terminate()
        proc_streamlit.wait()

    print("Both processes ended.")

if __name__ == '__main__':
    main()