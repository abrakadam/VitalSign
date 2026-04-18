/**
 * Библиотека для работы с FPS
 */

#ifndef FPS_LIB_H
#define FPS_LIB_H

#include <string>
#include <vector>

#ifdef _WIN32
    #include <windows.h>
#else
    #include <X11/Xlib.h>
#endif

class FPSLib {
private:
#ifdef _WIN32
    HWND targetWindow;
#else
    Display* display;
    Window targetWindow;
#endif
    
public:
    FPSLib();
    ~FPSLib();
    
    // Установить целевое окно по заголовку
    bool setTargetWindow(const std::string& title);
    
    // Получить текущий FPS
    int getCurrentFPS();
    
    // Получить информацию о окне
    std::vector<std::string> getWindowList();
    
    // Запустить мониторинг FPS
    void startMonitoring();
    
    // Остановить мониторинг
    void stopMonitoring();
};

#endif // FPS_LIB_H
