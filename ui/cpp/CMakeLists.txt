cmake_minimum_required(VERSION 3.10)
project(VitalSignCPP)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Добавляем путь к библиотекам
include_directories(${CMAKE_SOURCE_DIR}/../lib/cpp)

if(UNIX AND NOT APPLE)
    find_package(X11 REQUIRED)
    include_directories(${X11_INCLUDE_DIRS})
    link_directories(${X11_LIBRARY_DIRS})
endif()

# Добавляем библиотеки
add_subdirectory(../lib/cpp lib_cpp)

# Линкуем библиотеки
target_link_libraries(fps_monitor fps_lib)
target_link_libraries(system_monitor system_lib)

if(UNIX AND NOT APPLE)
    target_link_libraries(fps_monitor ${X11_LIBRARIES})
endif()
