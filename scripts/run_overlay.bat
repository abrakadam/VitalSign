@echo off
REM Скрипт запуска VitalSign Overlay для Windows

echo === Запуск VitalSign Overlay ===
echo.

REM Используем виртуальное окружение если оно существует
if exist venv (
    echo Использую виртуальное окружение...
    venv\Scripts\python gui_overlay.py
) else (
    echo Виртуальное окружение не найдено. Использую системный python...
    python gui_overlay.py
)
