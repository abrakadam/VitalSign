/**
 * Реализация библиотеки FPS
 */

#include "fps_lib.h"
#include <iostream>
#include <thread>
#include <chrono>
#include <algorithm>

FPSLib::FPSLib() {
#ifdef _WIN32
    targetWindow = NULL;
#else
    display = XOpenDisplay(NULL);
    if (!display) {
        std::cerr << "Не удалось открыть X display" << std::endl;
    }
    targetWindow = 0;
#endif
}

FPSLib::~FPSLib() {
#ifndef _WIN32
    if (display) {
        XCloseDisplay(display);
    }
#endif
}

bool FPSLib::setTargetWindow(const std::string& title) {
#ifdef _WIN32
    targetWindow = FindWindowA(NULL, title.c_str());
    return targetWindow != NULL;
#else
    // Linux: упрощенная реализация
    if (display) {
        // Здесь должна быть реализация поиска окна по заголовку
        std::cout << "Поиск окна: " << title << std::endl;
        return true;
    }
    return false;
#endif
}

int FPSLib::getCurrentFPS() {
    // В реальной реализации здесь должен быть код подсчета FPS
    // Это заглушка для демонстрации
    static int counter = 0;
    counter = (counter + 1) % 121; // 0-120
    return counter;
}

std::vector<std::string> FPSLib::getWindowList() {
    std::vector<std::string> windows;
    
#ifdef _WIN32
    EnumWindows([](HWND hwnd, LPARAM lParam) -> BOOL {
        char title[256];
        if (GetWindowTextA(hwnd, title, sizeof(title))) {
            std::vector<std::string>* windows = 
                reinterpret_cast<std::vector<std::string>*>(lParam);
            windows->push_back(title);
        }
        return TRUE;
    }, reinterpret_cast<LPARAM>(&windows));
#else
    // Linux: упрощенная реализация
    if (display) {
        windows.push_back("Пример окна 1");
        windows.push_back("Пример окна 2");
    }
#endif
    
    return windows;
}

void FPSLib::startMonitoring() {
    // Запуск мониторинга в отдельном потоке
    // Реализация должна быть добавлена
}

void FPSLib::stopMonitoring() {
    // Остановка мониторинга
    // Реализация должна быть добавлена
}
