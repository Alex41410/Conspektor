#!/usr/bin/env python3
"""
AI Summarizer Pro - Автоматический запуск
Проверяет и устанавливает зависимости, запускает backend и frontend
"""
import subprocess
import sys
import os
import time
import webbrowser
import platform
from pathlib import Path
import json

# Цвета для вывода (Windows)
if platform.system() == "Windows":
    try:
        import colorama
        colorama.init()
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        RED = "\033[91m"
        BLUE = "\033[94m"
        RESET = "\033[0m"
    except ImportError:
        GREEN = YELLOW = RED = BLUE = RESET = ""
else:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"

def print_status(message, color=GREEN):
    """Вывод статусного сообщения"""
    print(f"{color}[*] {message}{RESET}")

def print_error(message):
    """Вывод сообщения об ошибке"""
    print(f"{RED}[!] {message}{RESET}")

def print_warning(message):
    """Вывод предупреждения"""
    print(f"{YELLOW}[~] {message}{RESET}")

def check_command(command, name, install_hint=""):
    """Проверка наличия команды в PATH"""
    try:
        # Используем shell=True для Windows для правильной работы с PATH
        use_shell = platform.system() == "Windows"
        result = subprocess.run(
            [command, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            shell=use_shell
        )
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            print_status(f"{name} найден: {version}")
            return True
        else:
            print_error(f"{name} не найден")
            if install_hint:
                print_warning(f"  {install_hint}")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print_error(f"{name} не найден")
        if install_hint:
            print_warning(f"  {install_hint}")
        return False

def check_python():
    """Проверка Python"""
    if sys.version_info < (3, 8):
        print_error("Требуется Python 3.8 или выше")
        return False
    print_status(f"Python {sys.version.split()[0]} найден")
    return True

def check_node():
    """Проверка Node.js"""
    result = check_command(
        "node",
        "Node.js",
        "Установите Node.js с https://nodejs.org/"
    )
    if not result:
        print_error("\n" + "="*60)
        print_error("Node.js не найден!")
        print_error("="*60)
        print_warning("\nДля работы приложения необходимо установить Node.js:")
        print_warning("1. Перейдите на https://nodejs.org/")
        print_warning("2. Скачайте LTS версию (рекомендуется)")
        print_warning("3. Установите Node.js (npm установится автоматически)")
        print_warning("4. Перезапустите терминал после установки")
        print_warning("5. Запустите start.bat снова\n")
    return result

def check_npm():
    """Проверка npm"""
    # Используем shutil.which для более надежной проверки
    import shutil
    npm_path = shutil.which("npm")
    
    if npm_path:
        # Если npm найден через which, проверяем версию
        try:
            # Используем shell=True для Windows для правильной работы с PATH
            use_shell = platform.system() == "Windows"
            result = subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=use_shell
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                print_status(f"npm найден: {version}")
                return True
        except Exception as e:
            print_warning(f"Ошибка при проверке npm: {e}")
    
    # Если не нашли, пробуем стандартную проверку с shell=True для Windows
    try:
        use_shell = platform.system() == "Windows"
        result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            shell=use_shell
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print_status(f"npm найден: {version}")
            return True
    except Exception:
        pass
    
    # Если всё ещё не нашли, показываем ошибку
    print_error("\n" + "="*60)
    print_error("npm не найден!")
    print_error("="*60)
    print_warning("\nnpm должен устанавливаться вместе с Node.js.")
    print_warning("Если npm не найден после установки Node.js:")
    print_warning("1. Перезапустите терминал/командную строку")
    print_warning("2. Перезагрузите компьютер")
    print_warning("3. Проверьте, что Node.js добавлен в PATH")
    print_warning("4. Попробуйте переустановить Node.js\n")
    return False

def setup_backend():
    """Настройка backend"""
    backend_dir = Path("backend")
    venv_dir = backend_dir / "venv"
    requirements_file = backend_dir / "requirements.txt"
    
    print_status("Настройка backend...")
    
    # Создание виртуального окружения
    if not venv_dir.exists():
        print_status("Создание виртуального окружения...")
        result = subprocess.run(
            [sys.executable, "-m", "venv", str(venv_dir)],
            cwd=backend_dir.parent,
            capture_output=True
        )
        if result.returncode != 0:
            print_error("Не удалось создать виртуальное окружение")
            return False
    
    # Определение пути к Python в venv
    if platform.system() == "Windows":
        python_exe = venv_dir / "Scripts" / "python.exe"
        pip_exe = venv_dir / "Scripts" / "pip.exe"
    else:
        python_exe = venv_dir / "bin" / "python"
        pip_exe = venv_dir / "bin" / "pip"
    
    # Установка зависимостей
    if requirements_file.exists():
        print_status("Установка зависимостей backend...")
        result = subprocess.run(
            [str(pip_exe), "install", "-q", "-r", str(requirements_file)],
            cwd=backend_dir.parent,
            capture_output=True
        )
        if result.returncode != 0:
            print_error("Не удалось установить зависимости backend")
            if result.stderr:
                # Пробуем разные кодировки для Windows
                try:
                    error_msg = result.stderr.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        error_msg = result.stderr.decode('cp1251')
                    except UnicodeDecodeError:
                        try:
                            error_msg = result.stderr.decode('cp866')
                        except UnicodeDecodeError:
                            error_msg = result.stderr.decode('utf-8', errors='replace')
                print_error(error_msg)
            else:
                print_error("Неизвестная ошибка")
            return False
        print_status("Зависимости backend установлены")
    
    return str(python_exe)

def setup_frontend():
    """Настройка frontend"""
    frontend_dir = Path("frontend")
    node_modules = frontend_dir / "node_modules"
    package_json = frontend_dir / "package.json"
    
    print_status("Настройка frontend...")
    
    if not package_json.exists():
        print_error("package.json не найден")
        return False
    
    # Установка зависимостей
    if not node_modules.exists():
        print_status("Установка зависимостей frontend (это может занять несколько минут)...")
        result = subprocess.run(
            ["npm", "install"],
            cwd=frontend_dir,
            capture_output=True
        )
        if result.returncode != 0:
            print_error("Не удалось установить зависимости frontend")
            print_error(result.stderr.decode() if result.stderr else "Неизвестная ошибка")
            return False
        print_status("Зависимости frontend установлены")
    else:
        print_status("Зависимости frontend уже установлены")
    
    return True

def check_port_available(port):
    """Проверка доступности порта"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0  # True если порт свободен

def kill_process_on_port(port):
    """Попытка закрыть процесс на порту (Windows)"""
    if platform.system() == "Windows":
        try:
            # Используем netstat для поиска PID процесса на порту
            result = subprocess.run(
                f'netstat -ano | findstr :{port}',
                shell=True,
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout:
                # Парсим вывод и убиваем процесс
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) > 4:
                            pid = parts[-1]
                            try:
                                subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
                                print_warning(f"Закрыт процесс на порту {port} (PID: {pid})")
                                return True
                            except:
                                pass
        except Exception:
            pass
    return False

def check_lm_studio():
    """Проверка доступности LM Studio"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('localhost', 1234))
    sock.close()
    
    if result == 0:
        print_status("LM Studio доступен на порту 1234")
        return True
    else:
        print_warning("LM Studio не доступен на порту 1234")
        print_warning("  Убедитесь, что LM Studio запущен и локальный сервер активен")
        return False

def check_port_available(port):
    """Проверка доступности порта"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0  # True если порт свободен

def kill_process_on_port(port):
    """Попытка закрыть процесс на порту (Windows)"""
    if platform.system() == "Windows":
        try:
            # Используем netstat для поиска PID процесса на порту
            result = subprocess.run(
                f'netstat -ano | findstr :{port}',
                shell=True,
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout:
                # Парсим вывод и убиваем процесс
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) > 4:
                            pid = parts[-1]
                            try:
                                subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
                                print_warning(f"Закрыт процесс на порту {port} (PID: {pid})")
                            except:
                                pass
        except Exception:
            pass

def start_backend(python_exe):
    """Запуск backend"""
    backend_dir = Path("backend")
    main_py = backend_dir / "main.py"
    
    print_status("Запуск backend сервера...")
    
    # Сначала проверяем, что файл существует
    if not main_py.exists():
        print_error(f"Файл {main_py} не найден!")
        return None
    
    # Проверяем, свободен ли порт 8000
    if not check_port_available(8000):
        print_warning("Порт 8000 уже занят. Попытка освободить...")
        if kill_process_on_port(8000):
            time.sleep(2)
        if not check_port_available(8000):
            print_error("Порт 8000 все еще занят. Закройте процесс, использующий этот порт.")
            print_warning("Или перезапустите компьютер и попробуйте снова.")
            return None
    
    # Проверяем, свободен ли порт 8000
    if not check_port_available(8000):
        print_warning("Порт 8000 уже занят. Попытка освободить...")
        kill_process_on_port(8000)
        time.sleep(1)
        if not check_port_available(8000):
            print_error("Порт 8000 все еще занят. Закройте процесс, использующий этот порт, и попробуйте снова.")
            print_warning("Или перезапустите компьютер.")
            return None
    
    # Запуск в фоне с захватом ошибок для отладки
    try:
        if platform.system() == "Windows":
            # Сначала пробуем запустить с выводом ошибок для диагностики
            test_process = subprocess.Popen(
                [str(python_exe), str(main_py)],
                cwd=backend_dir.parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # Ждем немного
            time.sleep(2)
            if test_process.poll() is not None:
                # Процесс завершился - получаем ошибку
                stdout, stderr = test_process.communicate()
                if stderr:
                    print_error("Ошибка при запуске backend:")
                    print_error(stderr)
                elif stdout:
                    print_error("Вывод backend:")
                    print_error(stdout)
                return None
            
            # Если процесс еще работает, убиваем тестовый и запускаем нормальный
            test_process.terminate()
            test_process.wait()
            
            # Запускаем нормальный процесс
            process = subprocess.Popen(
                [str(python_exe), str(main_py)],
                cwd=backend_dir.parent,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            process = subprocess.Popen(
                [str(python_exe), str(main_py)],
                cwd=backend_dir.parent,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
    except AttributeError:
        # Fallback для старых версий Python
        process = subprocess.Popen(
            [str(python_exe), str(main_py)],
            cwd=backend_dir.parent,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print_error(f"Ошибка при запуске backend: {e}")
        return None
    
    # Ждем немного и проверяем, что процесс запустился
    time.sleep(3)
    if process.poll() is None:
        # Проверяем, что сервер действительно запустился, проверяя порт
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        
        if result == 0:
            print_status("Backend запущен на http://localhost:8000")
            return process
        else:
            print_warning("Backend процесс запущен, но порт 8000 еще не доступен. Подождите...")
            time.sleep(2)
            # Проверяем еще раз
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', 8000))
            sock.close()
            if result == 0:
                print_status("Backend запущен на http://localhost:8000")
                return process
            else:
                print_error("Backend не отвечает на порту 8000")
                process.terminate()
                return None
    else:
        print_error("Не удалось запустить backend - процесс завершился сразу")
        print_warning("Попробуйте запустить backend вручную для диагностики:")
        print_warning(f"  cd backend")
        print_warning(f"  {python_exe} main.py")
        return None

def start_frontend():
    """Запуск frontend"""
    frontend_dir = Path("frontend")
    
    print_status("Запуск frontend сервера...")
    
    # Проверяем, свободен ли порт 5173
    if not check_port_available(5173):
        print_warning("Порт 5173 уже занят. Попытка освободить...")
        if kill_process_on_port(5173):
            time.sleep(2)
        if not check_port_available(5173):
            print_error("Порт 5173 все еще занят. Закройте процесс, использующий этот порт.")
            return None
    
    # Запуск в фоне
    if platform.system() == "Windows":
        # На Windows нужно использовать shell=True и передавать команду как строку
        try:
            process = subprocess.Popen(
                "npm run dev",
                cwd=frontend_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except AttributeError:
            # Fallback для старых версий Python
            process = subprocess.Popen(
                "npm run dev",
                cwd=frontend_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=True
            )
    else:
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    
    # Ждем немного
    time.sleep(3)
    if process.poll() is None:
        print_status("Frontend запущен на http://localhost:5173")
        return process
    else:
        stdout, stderr = process.communicate()
        print_error("Не удалось запустить frontend")
        if stderr:
            print_error(stderr.decode())
        return None

def main():
    """Главная функция"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  AI Summarizer Pro - Автоматический запуск{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Проверка зависимостей
    print_status("Проверка зависимостей...")
    print()
    
    python_ok = check_python()
    print()
    
    if not python_ok:
        print_error("\n" + "="*60)
        print_error("❌ Python не найден!")
        print_error("="*60)
        print_warning("\nУстановите Python 3.8+ с https://www.python.org/")
        print_warning("⚠ ВАЖНО: При установке отметьте 'Add Python to PATH'")
        print_warning("\nПосле установки перезапустите терминал и запустите start.bat снова\n")
        input("Нажмите Enter для выхода...")
        return 1
    
    node_ok = check_node()
    print()
    
    if not node_ok:
        print_error("\n" + "="*60)
        print_error("❌ Node.js не найден!")
        print_error("="*60)
        print_warning("\nУстановите Node.js с https://nodejs.org/")
        print_warning("⚠ После установки ПЕРЕЗАПУСТИТЕ терминал или компьютер")
        print_warning("\nЗатем запустите start.bat снова\n")
        input("Нажмите Enter для выхода...")
        return 1
    
    npm_ok = check_npm()
    print()
    
    if not npm_ok:
        print_error("\n" + "="*60)
        print_error("❌ npm не найден!")
        print_error("="*60)
        print_warning("\nnpm должен устанавливаться вместе с Node.js.")
        print_warning("\nПопробуйте:")
        print_warning("1. ПЕРЕЗАПУСТИТЬ терминал/командную строку")
        print_warning("2. Перезагрузить компьютер")
        print_warning("3. Переустановить Node.js с https://nodejs.org/")
        print_warning("\nПосле этого запустите start.bat снова\n")
        input("Нажмите Enter для выхода...")
        return 1
    
    print_status("✓ Все зависимости найдены!")
    print()
    
    # Проверка LM Studio (не критично, но предупреждаем)
    print_status("\nПроверка LM Studio...")
    check_lm_studio()
    
    # Настройка backend
    print_status("\n" + "="*60)
    python_exe = setup_backend()
    if not python_exe:
        return 1
    
    # Настройка frontend
    print_status("\n" + "="*60)
    if not setup_frontend():
        return 1
    
    # Запуск серверов
    print_status("\n" + "="*60)
    print_status("Запуск серверов...")
    
    backend_process = start_backend(python_exe)
    if not backend_process:
        return 1
    
    time.sleep(2)  # Даем время backend запуститься
    
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        return 1
    
    # Открытие браузера
    print_status("\n" + "="*60)
    print_status("Ожидание запуска серверов...")
    time.sleep(3)
    
    try:
        webbrowser.open("http://localhost:5173")
        print_status("Браузер открыт")
    except Exception as e:
        print_warning(f"Не удалось открыть браузер: {e}")
        print_status("Откройте вручную: http://localhost:5173")
    
    print_status("\n" + "="*60)
    print_status("Приложение запущено!")
    print_status("Backend: http://localhost:8000")
    print_status("Frontend: http://localhost:5173")
    print_status("\nДля остановки нажмите Ctrl+C")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Ожидание завершения
    try:
        while True:
            time.sleep(1)
            # Проверяем, что процессы еще работают
            if backend_process.poll() is not None:
                print_error("Backend процесс завершился")
                break
            if frontend_process.poll() is not None:
                print_error("Frontend процесс завершился")
                break
    except KeyboardInterrupt:
        print_status("\nОстановка серверов...")
        backend_process.terminate()
        frontend_process.terminate()
        print_status("Серверы остановлены")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_status("\n\nПрервано пользователем")
        sys.exit(0)
    except Exception as e:
        print_error(f"\nНеожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
