#!/usr/bin/env python3
"""
Скрипт для проверки всех зависимостей AI Summarizer Pro
"""
import subprocess
import sys
import socket

def check_port(port):
    """Проверка доступности порта"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def check_command(command, name):
    """Проверка наличия команды в PATH"""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
        print(f"✓ {name} установлен")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"✗ {name} не найден")
        return False

def main():
    print("Проверка зависимостей AI Summarizer Pro\n")
    print("=" * 50)
    
    all_ok = True
    
    # Python зависимости
    print("\n1. Python зависимости:")
    try:
        import fastapi
        import pdfplumber
        import requests
        print("✓ Все Python пакеты установлены")
    except ImportError as e:
        print(f"✗ Отсутствует пакет: {e.name}")
        print("  Запустите: pip install -r backend/requirements.txt")
        all_ok = False
    
    # Системные утилиты
    print("\n2. Системные утилиты:")
    if not check_command("pandoc", "Pandoc"):
        print("  Установите Pandoc: https://pandoc.org/installing.html")
        all_ok = False
    
    # Сервисы
    print("\n3. Сервисы:")
    if check_port(1234):
        print("✓ LM Studio доступен на порту 1234")
    else:
        print("✗ LM Studio не доступен на порту 1234")
        print("  Запустите LM Studio и активируйте локальный сервер")
        all_ok = False
    
    print("\n" + "=" * 50)
    if all_ok:
        print("\n✓ Все зависимости установлены! Можно запускать приложение.")
        return 0
    else:
        print("\n✗ Некоторые зависимости отсутствуют. См. инструкции выше.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
