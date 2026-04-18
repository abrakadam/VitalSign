#ifndef HARDWARE_ANALYZER_H
#define HARDWARE_ANALYZER_H

#include <string>
#include <vector>
#include <map>

namespace HardwareAnalyzer {

struct CPUInfo {
    std::string model;
    std::string vendor;
    int cores;
    int threads;
    double frequency_mhz;
    std::string architecture;
    std::vector<std::string> features;
};

struct MemoryInfo {
    double total_gb;
    double available_gb;
    double used_gb;
    int speed_mhz;
    std::string type;
    int slots;
    std::vector<std::string> modules;
};

struct DiskInfo {
    std::string device;
    std::string model;
    double size_gb;
    double used_gb;
    std::string filesystem;
    std::string mount_point;
    bool is_ssd;
    std::string interface;
};

struct GPUInfo {
    std::string vendor;
    std::string model;
    double vram_gb;
    double current_clock_mhz;
    double max_clock_mhz;
    int temperature_c;
    double utilization_percent;
    std::string driver_version;
    std::string cuda_version;
};

class HardwareAnalyzerLib {
public:
    HardwareAnalyzerLib();
    ~HardwareAnalyzerLib();
    
    // CPU анализ
    CPUInfo get_cpu_info();
    
    // Память анализ
    MemoryInfo get_memory_info();
    
    // Диски анализ
    std::vector<DiskInfo> get_disk_info();
    
    // GPU анализ
    std::vector<GPUInfo> get_gpu_info();
    
    // Полная информация о железе
    std::map<std::string, std::string> get_full_hardware_info();
    
private:
    bool read_file(const std::string& path, std::string& output);
    std::string read_file(const std::string& path, const std::string& default_value);
    bool file_exists(const std::string& path);
    std::vector<std::string> read_lines(const std::string& path);
    std::string execute_command(const std::string& command);
};

} // namespace HardwareAnalyzer

#endif // HARDWARE_ANALYZER_H
