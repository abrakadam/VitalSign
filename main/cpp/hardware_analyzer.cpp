#include "hardware_analyzer.h"
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <unistd.h>
#include <sys/utsname.h>
#include <dirent.h>
#include <sys/statvfs.h>

namespace HardwareAnalyzer {

HardwareAnalyzerLib::HardwareAnalyzerLib() {
}

HardwareAnalyzerLib::~HardwareAnalyzerLib() {
}

bool HardwareAnalyzerLib::read_file(const std::string& path, std::string& output) {
    std::ifstream file(path);
    if (!file.is_open()) {
        return false;
    }
    std::getline(file, output);
    file.close();
    return true;
}

std::string HardwareAnalyzerLib::read_file(const std::string& path, const std::string& default_value) {
    std::ifstream file(path);
    if (!file.is_open()) {
        return default_value;
    }
    std::string content;
    std::getline(file, content);
    file.close();
    return content;
}

bool HardwareAnalyzerLib::file_exists(const std::string& path) {
    std::ifstream file(path);
    return file.good();
}

std::vector<std::string> HardwareAnalyzerLib::read_lines(const std::string& path) {
    std::vector<std::string> lines;
    std::ifstream file(path);
    if (!file.is_open()) {
        return lines;
    }
    std::string line;
    while (std::getline(file, line)) {
        lines.push_back(line);
    }
    file.close();
    return lines;
}

std::string HardwareAnalyzerLib::execute_command(const std::string& command) {
    FILE* pipe = popen(command.c_str(), "r");
    if (!pipe) {
        return "";
    }
    
    char buffer[128];
    std::string result = "";
    while (fgets(buffer, sizeof(buffer), pipe) != nullptr) {
        result += buffer;
    }
    pclose(pipe);
    
    // Удаляем перенос строки в конце
    if (!result.empty() && result.back() == '\n') {
        result.pop_back();
    }
    return result;
}

CPUInfo HardwareAnalyzerLib::get_cpu_info() {
    CPUInfo info;
    
    // Читаем /proc/cpuinfo
    auto lines = read_lines("/proc/cpuinfo");
    for (const auto& line : lines) {
        if (line.find("model name") == 0) {
            size_t pos = line.find(':');
            if (pos != std::string::npos) {
                info.model = line.substr(pos + 2);
            }
        } else if (line.find("vendor_id") == 0) {
            size_t pos = line.find(':');
            if (pos != std::string::npos) {
                info.vendor = line.substr(pos + 2);
            }
        } else if (line.find("cpu cores") == 0) {
            size_t pos = line.find(':');
            if (pos != std::string::npos) {
                info.cores = std::stoi(line.substr(pos + 2));
            }
        } else if (line.find("siblings") == 0) {
            size_t pos = line.find(':');
            if (pos != std::string::npos) {
                info.threads = std::stoi(line.substr(pos + 2));
            }
        } else if (line.find("flags") == 0) {
            size_t pos = line.find(':');
            if (pos != std::string::npos) {
                std::string flags = line.substr(pos + 2);
                std::istringstream iss(flags);
                std::string flag;
                while (iss >> flag) {
                    info.features.push_back(flag);
                }
            }
        }
    }
    
    // Частота из /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq
    std::string freq_str = read_file("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq", "0");
    info.frequency_mhz = std::stod(freq_str) / 1000.0;
    
    // Архитектура
    struct utsname uname_info;
    if (uname(&uname_info) == 0) {
        info.architecture = uname_info.machine;
    }
    
    return info;
}

MemoryInfo HardwareAnalyzerLib::get_memory_info() {
    MemoryInfo info;
    
    // Читаем /proc/meminfo
    auto lines = read_lines("/proc/meminfo");
    for (const auto& line : lines) {
        if (line.find("MemTotal:") == 0) {
            std::istringstream iss(line);
            std::string label;
            long long mem_kb;
            iss >> label >> mem_kb;
            info.total_gb = mem_kb / (1024.0 * 1024.0);
        } else if (line.find("MemAvailable:") == 0) {
            std::istringstream iss(line);
            std::string label;
            long long mem_kb;
            iss >> label >> mem_kb;
            info.available_gb = mem_kb / (1024.0 * 1024.0);
        }
    }
    
    info.used_gb = info.total_gb - info.available_gb;
    
    // Скорость памяти из dmidecode (требует root)
    std::string speed_str = execute_command("sudo dmidecode -t memory 2>/dev/null | grep Speed | head -1");
    if (!speed_str.empty()) {
        size_t pos = speed_str.find(':');
        if (pos != std::string::npos) {
            info.speed_mhz = std::stoi(speed_str.substr(pos + 2));
        }
    }
    
    return info;
}

std::vector<DiskInfo> HardwareAnalyzerLib::get_disk_info() {
    std::vector<DiskInfo> disks;
    
    // Читаем /proc/mounts
    auto lines = read_lines("/proc/mounts");
    for (const auto& line : lines) {
        std::istringstream iss(line);
        std::string device, mount_point, filesystem;
        iss >> device >> mount_point >> filesystem;
        
        // Пропускаем системные mounts
        if (device.find("/dev/") != 0 || device.find("loop") != std::string::npos) {
            continue;
        }
        
        DiskInfo disk;
        disk.device = device;
        disk.mount_point = mount_point;
        disk.filesystem = filesystem;
        
        // Размер через statvfs
        struct statvfs stat;
        if (statvfs(mount_point.c_str(), &stat) == 0) {
            disk.size_gb = (stat.f_blocks * stat.f_frsize) / (1024.0 * 1024.0 * 1024.0);
            disk.used_gb = ((stat.f_blocks - stat.f_bfree) * stat.f_frsize) / (1024.0 * 1024.0 * 1024.0);
        }
        
        // Модель диска
        std::string device_name = device.substr(device.find_last_of('/') + 1);
        std::string model_path = "/sys/block/" + device_name + "/device/model";
        disk.model = read_file(model_path, "Unknown");
        
        // Проверка на SSD
        std::string rotational_path = "/sys/block/" + device_name + "/queue/rotational";
        std::string rotational = read_file(rotational_path, "1");
        disk.is_ssd = (rotational == "0");
        
        disks.push_back(disk);
    }
    
    return disks;
}

std::vector<GPUInfo> HardwareAnalyzerLib::get_gpu_info() {
    std::vector<GPUInfo> gpus;
    
    // Проверяем NVIDIA через nvidia-smi
    std::string nvidia_output = execute_command("nvidia-smi --query-gpu=name,memory.total,clocks.current.graphics,clocks.max.graphics,temperature.gpu,utilization.gpu,driver_version,cuda.version --format=csv,noheader,nounits 2>/dev/null");
    
    if (!nvidia_output.empty()) {
        std::istringstream iss(nvidia_output);
        std::string line;
        while (std::getline(iss, line)) {
            GPUInfo gpu;
            std::istringstream line_iss(line);
            std::string token;
            
            std::getline(line_iss, token, ',');
            gpu.model = token;
            
            std::getline(line_iss, token, ',');
            gpu.vram_gb = std::stod(token) / 1024.0;
            
            std::getline(line_iss, token, ',');
            gpu.current_clock_mhz = std::stod(token);
            
            std::getline(line_iss, token, ',');
            gpu.max_clock_mhz = std::stod(token);
            
            std::getline(line_iss, token, ',');
            gpu.temperature_c = std::stoi(token);
            
            std::getline(line_iss, token, ',');
            gpu.utilization_percent = std::stod(token);
            
            std::getline(line_iss, token, ',');
            gpu.driver_version = token;
            
            std::getline(line_iss, token, ',');
            gpu.cuda_version = token;
            
            gpu.vendor = "NVIDIA";
            gpus.push_back(gpu);
        }
    }
    
    // Проверяем AMD через lspci
    std::string amd_output = execute_command("lspci | grep -i vga");
    if (!amd_output.empty() && gpus.empty()) {
        GPUInfo gpu;
        gpu.vendor = "AMD";
        gpu.model = amd_output;
        gpu.utilization_percent = 0;
        gpus.push_back(gpu);
    }
    
    // Проверяем Intel через lspci
    std::string intel_output = execute_command("lspci | grep -i 'Intel.*VGA'");
    if (!intel_output.empty() && gpus.empty()) {
        GPUInfo gpu;
        gpu.vendor = "Intel";
        gpu.model = intel_output;
        gpu.utilization_percent = 0;
        gpus.push_back(gpu);
    }
    
    return gpus;
}

std::map<std::string, std::string> HardwareAnalyzerLib::get_full_hardware_info() {
    std::map<std::string, std::string> info;
    
    // CPU
    CPUInfo cpu = get_cpu_info();
    info["cpu_model"] = cpu.model;
    info["cpu_vendor"] = cpu.vendor;
    info["cpu_cores"] = std::to_string(cpu.cores);
    info["cpu_threads"] = std::to_string(cpu.threads);
    info["cpu_frequency_mhz"] = std::to_string(cpu.frequency_mhz);
    
    // Память
    MemoryInfo mem = get_memory_info();
    info["memory_total_gb"] = std::to_string(mem.total_gb);
    info["memory_used_gb"] = std::to_string(mem.used_gb);
    info["memory_speed_mhz"] = std::to_string(mem.speed_mhz);
    
    // Диски
    auto disks = get_disk_info();
    info["disk_count"] = std::to_string(disks.size());
    for (size_t i = 0; i < disks.size(); ++i) {
        info["disk_" + std::to_string(i) + "_device"] = disks[i].device;
        info["disk_" + std::to_string(i) + "_model"] = disks[i].model;
        info["disk_" + std::to_string(i) + "_size_gb"] = std::to_string(disks[i].size_gb);
    }
    
    // GPU
    auto gpus = get_gpu_info();
    info["gpu_count"] = std::to_string(gpus.size());
    for (size_t i = 0; i < gpus.size(); ++i) {
        info["gpu_" + std::to_string(i) + "_vendor"] = gpus[i].vendor;
        info["gpu_" + std::to_string(i) + "_model"] = gpus[i].model;
        info["gpu_" + std::to_string(i) + "_vram_gb"] = std::to_string(gpus[i].vram_gb);
    }
    
    return info;
}

} // namespace HardwareAnalyzer
