#include <iostream>
#include <string>
#include <thread>
#include <chrono>
#include "fps_lib.h"

int main() {
    std::cout << "=== FPS Monitor ===" << std::endl;
    std::cout << "Использование библиотеки fps_lib" << std::endl << std::endl;
    
    FPSLib fpsLib;
    
    // Получить список окон
    std::cout << "Доступные окна:" << std::endl;
    auto windows = fpsLib.getWindowList();
    for (size_t i = 0; i < windows.size() && i < 10; ++i) {
        std::cout << i + 1 << ". " << windows[i] << std::endl;
    }
    
    // Запустить мониторинг
    fpsLib.startMonitoring();
    
    std::cout << "\nМониторинг FPS запущен..." << std::endl;
    std::cout << "Нажмите Enter для остановки..." << std::endl;
    std::cin.get();
    
    fpsLib.stopMonitoring();
    
    return 0;
}
