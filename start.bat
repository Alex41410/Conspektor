@echo off
chcp 65001 >nul 2>&1
title AI Summarizer Pro - Запуск

echo.
echo ============================================================
echo   AI Summarizer Pro - Автоматический запуск
echo ============================================================
echo.

echo [*] Проверка зависимостей...
echo.

REM Проверка Python
echo [*] Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python не найден!
    echo.
    echo ============================================================
    echo   [ERROR] Python не найден!
    echo ============================================================
    echo.
    echo Установите Python 3.8+ с https://www.python.org/
    echo.
    echo ВАЖНО: При установке отметьте "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
python --version
echo [OK] Python найден
echo.

REM Проверка Node.js
echo [*] Проверка Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js не найден!
    echo.
    echo ============================================================
    echo   [ERROR] Node.js не найден!
    echo ============================================================
    echo.
    echo Установите Node.js с https://nodejs.org/
    echo.
    echo После установки перезапустите терминал или компьютер
    echo.
    pause
    exit /b 1
)
node --version
echo [OK] Node.js найден
echo.

REM Проверка npm
echo [*] Проверка npm...
call npm --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm не найден!
    echo.
    echo ============================================================
    echo   [ERROR] npm не найден!
    echo ============================================================
    echo.
    echo npm должен устанавливаться вместе с Node.js
    echo.
    echo Попробуйте:
    echo 1. Перезапустить терминал
    echo 2. Переустановить Node.js с https://nodejs.org/
    echo 3. Перезагрузить компьютер
    echo.
    pause
    exit /b 1
)
call npm --version
echo [OK] npm найден
echo.

echo ============================================================
echo [OK] Все зависимости найдены!
echo ============================================================
echo.
echo [*] Запуск приложения...
echo.
echo [*] Запуск Python скрипта start.py...
echo.

REM Запуск Python скрипта
python start.py
set PYTHON_EXIT=%errorlevel%

if %PYTHON_EXIT% neq 0 (
    echo.
    echo ============================================================
    echo [ERROR] Ошибка запуска приложения
    echo ============================================================
    echo.
    pause
    exit /b %PYTHON_EXIT%
)

echo.
echo ============================================================
echo Приложение завершено
echo ============================================================
pause
