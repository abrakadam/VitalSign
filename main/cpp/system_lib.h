/**
 * Библиотека для системного мониторинга на C++
 */

#ifndef SYSTEM_LIB_H
#define SYSTEM_LIB_H

#include <string>
#include <vector>

#ifdef _WIN32
    #include <windows.h>
    #include <psapi.h>
#else
    #include <sys/sysinfo.h>
    #include <sys/statvfs.h>
#endif

struct SystemStats {
    double cpu_usage;
    double memory_usage;
    double memory_total;
    double disk_usage;
    double disk_total;
    unsigned long network_sent;
    unsigned long network_recv;
};

class SystemLib {
private:
    unsigned long last_network_sent;
    unsigned long last_network_recv;
    
public:
    SystemLib();
    
    // Получить статистику системы
    SystemStats getSystemStats();
    
    // Получить использование CPU
    double getCPUUsage();
    
    // Получить использование памяти
    double getMemoryUsage();
    
    // Получить общую память
    double getTotalMemory();
    
    // Получить использование диска
    double getDiskUsage(const std::string& path = "/");
    
    // Получить общий объем диска
    double getTotalDisk(const std::string& path = "/");
    
    // Получить сетевую статистику
    void getNetworkStats(unsigned long& sent, unsigned long& recv);
    
    // Получить список процессов
    std::vector<std::string> getProcessList();
    
    // Получить температуру CPU (если доступно)
    double getCPUTemperature();
};

#endif // SYSTEM_LIB_H
