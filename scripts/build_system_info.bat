@echo off
REM Скрипт для сборки C++ библиотеки системной информации (Windows)

echo === Сборка C++ System Info Library ===
echo.

REM Создаем папку для сборки
if not exist build\lib mkdir build\lib
cd build

REM Настраиваем CMake
echo Настраиваем CMake...
cmake -DCMAKE_BUILD_TYPE=Release ..

REM Собираем
echo Собираем...
cmake --build . --config Release

echo === Сборка завершена ===
