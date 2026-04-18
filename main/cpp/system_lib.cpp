/**
 * Реализация библиотеки системного мониторинга на C++
 */

#include "system_lib.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <algorithm>

SystemLib::SystemLib() {
    last_network_sent = 0;
    last_network_recv = 0;
}

SystemStats SystemLib::getSystemStats() {
    SystemStats stats;
    stats.cpu_usage = getCPUUsage();
    stats.memory_usage = getMemoryUsage();
    stats.memory_total = getTotalMemory();
    stats.disk_usage = getDiskUsage();
    stats.disk_total = getTotalDisk();
    getNetworkStats(stats.network_sent, stats.network_recv);
    return stats;
}

double SystemLib::getCPUUsage() {
#ifdef _WIN32
    FILETIME idleTime, kernelTime, userTime;
    if (GetSystemTimes(&idleTime, &kernelTime, &userTime)) {
        static ULONGLONG last_idle = 0, last_kernel = 0, last_user = 0;
        
        ULONGLONG idle = ((ULONGLONG)idleTime.dwLowDateTime | 
                         ((ULONGLONG)idleTime.dwHighDateTime << 32)) / 10000;
        ULONGLONG kernel = ((ULONGLONG)kernelTime.dwLowDateTime | 
                           ((ULONGLONG)kernelTime.dwHighDateTime << 32)) / 10000;
        ULONGLONG user = ((ULONGLONG)userTime.dwLowDateTime | 
                         ((ULONGLONG)userTime.dwHighDateTime << 32)) / 10000;
        
        if (last_idle != 0) {
            ULONGLONG total_idle = idle - last_idle;
            ULONGLONG total_kernel = kernel - last_kernel;
            ULONGLONG total_user = user - last_user;
            ULONGLONG total_system = total_kernel + total_user;
            
            last_idle = idle;
            last_kernel = kernel;
            last_user = user;
            
            if (total_system > 0) {
                return 100.0 * (1.0 - (double)total_idle / (double)total_system);
            }
        }
        
        last_idle = idle;
        last_kernel = kernel;
        last_user = user;
    }
    return 0.0;
#else
    // Linux: чтение из /proc/stat
    std::ifstream file("/proc/stat");
    if (file.is_open()) {
        std::string line;
        if (std::getline(file, line)) {
            std::istringstream iss(line);
            std::string cpu;
            unsigned long user, nice, system, idle, iowait, irq, softirq, steal;
            
            iss >> cpu >> user >> nice >> system >> idle >> iowait >> irq >> softirq >> steal;
            
            static unsigned long last_total = 0, last_idle = 0;
            
            unsigned long total = user + nice + system + idle + iowait + irq + softirq + steal;
            
            if (last_total != 0) {
                unsigned long total_diff = total - last_total;
                unsigned long idle_diff = idle - last_idle;
                
                last_total = total;
                last_idle = idle;
                
                if (total_diff > 0) {
                    return 100.0 * (1.0 - (double)idle_diff / (double)total_diff);
                }
            }
            
            last_total = total;
            last_idle = idle;
        }
        file.close();
    }
    return 0.0;
#endif
}

double SystemLib::getMemoryUsage() {
#ifdef _WIN32
    MEMORYSTATUSEX status;
    status.dwLength = sizeof(status);
    if (GlobalMemoryStatusEx(&status)) {
        return (double)status.ullTotalPhys - (double)status.ullAvailPhys;
    }
    return 0.0;
#else
    struct sysinfo info;
    if (sysinfo(&info) == 0) {
        return (info.totalram - info.freeram) / (1024.0 * 1024.0); // MB
    }
    return 0.0;
#endif
}

double SystemLib::getTotalMemory() {
#ifdef _WIN32
    MEMORYSTATUSEX status;
    status.dwLength = sizeof(status);
    if (GlobalMemoryStatusEx(&status)) {
        return (double)status.ullTotalPhys / (1024.0 * 1024.0); // MB
    }
    return 0.0;
#else
    struct sysinfo info;
    if (sysinfo(&info) == 0) {
        return info.totalram / (1024.0 * 1024.0); // MB
    }
    return 0.0;
#endif
}

double SystemLib::getDiskUsage(const std::string& path) {
#ifdef _WIN32
    ULARGE_INTEGER free, total;
    if (GetDiskFreeSpaceExA(path.c_str(), &free, &total, NULL)) {
        return (double)(total.QuadPart - free.QuadPart) / (1024.0 * 1024.0 * 1024.0); // GB
    }
    return 0.0;
#else
    struct statvfs stat;
    if (statvfs(path.c_str(), &stat) == 0) {
        unsigned long long total = stat.f_blocks * stat.f_frsize;
        unsigned long long free = stat.f_bfree * stat.f_frsize;
        return (double)(total - free) / (1024.0 * 1024.0 * 1024.0); // GB
    }
    return 0.0;
#endif
}

double SystemLib::getTotalDisk(const std::string& path) {
#ifdef _WIN32
    ULARGE_INTEGER free, total;
    if (GetDiskFreeSpaceExA(path.c_str(), &free, &total, NULL)) {
        return (double)total.QuadPart / (1024.0 * 1024.0 * 1024.0); // GB
    }
    return 0.0;
#else
    struct statvfs stat;
    if (statvfs(path.c_str(), &stat) == 0) {
        unsigned long long total = stat.f_blocks * stat.f_frsize;
        return (double)total / (1024.0 * 1024.0 * 1024.0); // GB
    }
    return 0.0;
#endif
}

void SystemLib::getNetworkStats(unsigned long& sent, unsigned long& recv) {
#ifdef _WIN32
    // Windows: требуется более сложная реализация через GetIfTable2
    sent = 0;
    recv = 0;
#else
    // Linux: чтение из /proc/net/dev
    std::ifstream file("/proc/net/dev");
    if (file.is_open()) {
        std::string line;
        unsigned long total_sent = 0, total_recv = 0;
        
        // Пропускаем заголовки
        std::getline(file, line);
        std::getline(file, line);
        
        while (std::getline(file, line)) {
            std::istringstream iss(line);
            std::string interface;
            unsigned long bytes_recv, packets_recv, errs_recv, drop_recv, 
                         fifo_recv, frame_recv, compressed_recv, 
                         multicast_recv, bytes_sent, packets_sent;
            
            iss >> interface;
            iss >> bytes_recv >> packets_recv >> errs_recv >> drop_recv 
                >> fifo_recv >> frame_recv >> compressed_recv >> multicast_recv 
                >> bytes_sent >> packets_sent;
            
            total_recv += bytes_recv;
            total_sent += bytes_sent;
        }
        
        sent = total_sent;
        recv = total_recv;
        file.close();
    } else {
        sent = 0;
        recv = 0;
    }
#endif
}

std::vector<std::string> SystemLib::getProcessList() {
    std::vector<std::string> processes;
    
#ifdef _WIN32
    HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (snapshot != INVALID_HANDLE_VALUE) {
        PROCESSENTRY32 entry;
        entry.dwSize = sizeof(entry);
        
        if (Process32First(snapshot, &entry)) {
            do {
                processes.push_back(entry.szExeFile);
            } while (Process32Next(snapshot, &entry));
        }
        CloseHandle(snapshot);
    }
#else
    // Linux: чтение из /proc
    DIR* dir = opendir("/proc");
    if (dir) {
        struct dirent* entry;
        while ((entry = readdir(dir)) != NULL) {
            if (entry->d_name[0] >= '0' && entry->d_name[0] <= '9') {
                std::string cmdline_path = "/proc/" + std::string(entry->d_name) + "/cmdline";
                std::ifstream file(cmdline_path);
                if (file.is_open()) {
                    std::string cmdline;
                    std::getline(file, cmdline);
                    if (!cmdline.empty()) {
                        processes.push_back(cmdline);
                    }
                    file.close();
                }
            }
        }
        closedir(dir);
    }
#endif
    
    return processes;
}

double SystemLib::getCPUTemperature() {
#ifdef _WIN32
    // Windows: требует WMI или другие методы
    return 0.0;
#else
    // Linux: чтение из /sys/class/thermal
    std::ifstream file("/sys/class/thermal/thermal_zone0/temp");
    if (file.is_open()) {
        int temp;
        file >> temp;
        file.close();
        return temp / 1000.0; // Конвертируем из миллиградусов в градусы
    }
    return 0.0;
#endif
}
