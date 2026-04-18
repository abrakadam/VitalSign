/**
 * C++ утилита для системного мониторинга (консольная версия)
 */

#include <iostream>
#include <chrono>
#include <thread>
#include "../lib/cpp/system_lib.h"

void printSeparator() {
    std::cout << "========================================" << std::endl;
}

void printSystemStats(const SystemStats& stats) {
    std::cout << "\n=== Системная статистика ===" << std::endl;
    std::cout << "CPU: " << stats.cpu_usage << "%" << std::endl;
    std::cout << "Память: " << stats.memory_usage << " MB / " 
              << stats.memory_total << " MB" << std::endl;
    std::cout << "Диск: " << stats.disk_usage << " GB / " 
              << stats.disk_total << " GB" << std::endl;
    std::cout << "Сеть (отправлено): " << stats.network_sent / (1024 * 1024) << " MB" << std::endl;
    std::cout << "Сеть (получено): " << stats.network_recv / (1024 * 1024) << " MB" << std::endl;
}

int main() {
    std::cout << "=== VitalSign C++ System Monitor ===" << std::endl;
    printSeparator();
    
    SystemLib sysLib;
    
    std::cout << "\nТестирование библиотеки системного мониторинга..." << std::endl;
    
    // Получаем статистику
    SystemStats stats = sysLib.getSystemStats();
    printSystemStats(stats);
    
    // Тестирование отдельных функций
    std::cout << "\n=== Детальное тестирование ===" << std::endl;
    
    double cpu = sysLib.getCPUUsage();
    std::cout << "CPU (отдельно): " << cpu << "%" << std::endl;
    
    double mem_usage = sysLib.getMemoryUsage();
    double mem_total = sysLib.getTotalMemory();
    std::cout << "Память (отдельно): " << mem_usage << " MB / " 
              << mem_total << " MB" << std::endl;
    
    double disk_usage = sysLib.getDiskUsage();
    double disk_total = sysLib.getTotalDisk();
    std::cout << "Диск (отдельно): " << disk_usage << " GB / " 
              << disk_total << " GB" << std::endl;
    
    double temp = sysLib.getCPUTemperature();
    if (temp > 0) {
        std::cout << "Температура CPU: " << temp << "°C" << std::endl;
    } else {
        std::cout << "Температура CPU: недоступно" << std::endl;
    }
    
    // Список процессов
    std::cout << "\n=== Процессы (первые 10) ===" << std::endl;
    auto processes = sysLib.getProcessList();
    for (size_t i = 0; i < std::min(processes.size(), (size_t)10); ++i) {
        std::cout << i + 1 << ". " << processes[i] << std::endl;
    }
    
    std::cout << "\nВсего процессов: " << processes.size() << std::endl;
    
    // Непрерывный мониторинг
    std::cout << "\n=== Непрерывный мониторинг ===" << std::endl;
    std::cout << "Нажмите Enter для остановки..." << std::endl;
    
    std::cin.get();
    
    return 0;
}
