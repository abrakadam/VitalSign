@echo off
REM Скрипт запуска GUI версии VitalSign для Windows

echo === Запуск VitalSign GUI ===
echo.

REM Проверка установки PyQt6
python -c "import PyQt6" 2>nul
if %errorlevel% neq 0 (
    echo PyQt6 не установлен. Устанавливаю...
    pip install PyQt6
)

REM Запуск GUI
python gui_main.py
