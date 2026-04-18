cmake_minimum_required(VERSION 3.10)

# Компилируем system_info_lib как статическую библиотеку
add_library(system_info_lib STATIC
    system_info_lib.cpp
)

# Устанавливаем include директорию
target_include_directories(system_info_lib PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)
