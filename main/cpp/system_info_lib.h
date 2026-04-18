#ifndef SYSTEM_INFO_LIB_H
#define SYSTEM_INFO_LIB_H

#include <string>
#include <vector>
#include <map>

namespace SystemInfo {

struct HardwareInfo {
    std::string system_vendor;
    std::string product_name;
    std::string product_version;
    std::string board_vendor;
    std::string board_name;
    std::string bios_vendor;
    std::string bios_version;
    std::string bios_date;
    std::string cpu_model;
    std::string total_memory;
};

struct OSInfo {
    std::string system;
    std::string release;
    std::string version;
    std::string machine;
    std::string hostname;
    std::string distribution;
    std::string kernel_version;
};

struct EnvironmentInfo {
    std::string desktop_environment;
    std::string display_server;
    std::string shell;
    std::string window_manager;
};

struct BootloaderInfo {
    std::string name;
    std::string path;
    bool active;
};

class SystemInfoLib {
public:
    SystemInfoLib();
    ~SystemInfoLib();
    
    // Получить информацию о железе
    HardwareInfo get_hardware_info();
    
    // Получить информацию об ОС
    OSInfo get_os_info();
    
    // Получить информацию об окружении
    EnvironmentInfo get_environment_info();
    
    // Получить список загрузчиков
    std::vector<BootloaderInfo> get_bootloaders();
    
    // Получить список установленных ОС
    std::vector<std::string> get_installed_os();
    
    // Получить информацию о BIOS
    std::map<std::string, std::string> get_bios_info();
    
    // Получить информацию о драйверах
    std::vector<std::string> get_drivers();
    
    // Получить серийный номер
    std::string get_serial_number();
    
private:
    bool read_dmi_file(const std::string& path, std::string& output);
    std::string read_file(const std::string& path, const std::string& default_value);
    bool file_exists(const std::string& path);
};

} // namespace SystemInfo

#endif // SYSTEM_INFO_LIB_H
