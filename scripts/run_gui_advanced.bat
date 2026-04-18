@echo off
REM Скрипт запуска расширенной GUI версии VitalSign для Windows

echo === Запуск VitalSign Advanced GUI ===
echo.

REM Используем виртуальное окружение если оно существует
if exist venv (
    echo Использую виртуальное окружение...
    venv\Scripts\python gui_advanced.py
) else (
    echo Виртуальное окружение не найдено. Использую системный python...
    REM Проверка установки PyQt6
    python -c "import PyQt6, matplotlib" 2>nul
    if %errorlevel% neq 0 (
        echo PyQt6 или matplotlib не установлен. Создаю виртуальное окружение и устанавливаю...
        python -m venv venv
        venv\Scripts\pip install -r requirements.txt
    )
    python gui_advanced.py
)
