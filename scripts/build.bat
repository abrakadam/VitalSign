@echo off
REM Скрипт сборки проекта VitalSign для Windows

echo === Сборка VitalSign ===
echo.

REM Проверка Python
echo 1. Проверка Python зависимостей...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Ошибка: Python не установлен
    exit /b 1
)

echo Установка Python зависимостей...
pip install -r requirements.txt

REM Проверка PyQt6
echo.
echo 2. Проверка PyQt6 для GUI...
python -c "import PyQt6" 2>nul
if %errorlevel% neq 0 (
    echo PyQt6 не установлен. Устанавливаю...
    pip install PyQt6
)

REM Сборка C++ части
echo.
echo 3. Сборка C++ модуля...
cd cpp
if not exist build mkdir build
cd build
cmake ..
cmake --build .
cd ..\..

echo.
echo === Сборка завершена успешно ===
echo.
echo Для запуска:
echo   GUI:       python gui_main.py
echo   Консоль:   python main.py
echo   C++:       cpp\build\Debug\fps_monitor.exe
