@echo off
REM Скрипт запуска Discord-style VitalSign Overlay для Windows

echo === Запуск Discord-style VitalSign Overlay ===
echo.

REM Используем виртуальное окружение если оно существует
if exist venv (
    echo Использую виртуальное окружение...
    venv\Scripts\python gui_discord_overlay.py
) else (
    echo Виртуальное окружение не найдено. Использую системный python...
    python gui_discord_overlay.py
)
