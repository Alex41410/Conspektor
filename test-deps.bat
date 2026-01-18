@echo off
echo ============================================================
echo   Проверка зависимостей
echo ============================================================
echo.

echo Проверка Python:
python --version
if errorlevel 1 (
    echo [ERROR] Python не найден!
) else (
    echo [OK] Python найден
)
echo.

echo Проверка Node.js:
node --version
if errorlevel 1 (
    echo [ERROR] Node.js не найден!
) else (
    echo [OK] Node.js найден
)
echo.

echo Проверка npm:
npm --version
if errorlevel 1 (
    echo [ERROR] npm не найден!
) else (
    echo [OK] npm найден
)
echo.

echo ============================================================
pause
