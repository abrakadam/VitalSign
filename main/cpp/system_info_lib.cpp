#include "system_info_lib.h"
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <unistd.h>
#include <sys/utsname.h>
#include <dirent.h>

namespace SystemInfo {

SystemInfoLib::SystemInfoLib() {
}

SystemInfoLib::~SystemInfoLib() {
}

bool SystemInfoLib::read_dmi_file(const std::string& path, std::string& output) {
    std::ifstream file(path);
    if (!file.is_open()) {
        return false;
    }
    std::getline(file, output);
    file.close();
    return true;
}

std::string SystemInfoLib::read_file(const std::string& path, const std::string& default_value) {
    std::ifstream file(path);
    if (!file.is_open()) {
        return default_value;
    }
    std::string content;
    std::getline(file, content);
    file.close();
    return content;
}

bool SystemInfoLib::file_exists(const std::string& path) {
    std::ifstream file(path);
    return file.good();
}

HardwareInfo SystemInfoLib::get_hardware_info() {
    HardwareInfo info;
    
    info.system_vendor = read_file("/sys/class/dmi/id/sys_vendor", "N/A");
    info.product_name = read_file("/sys/class/dmi/id/product_name", "N/A");
    info.product_version = read_file("/sys/class/dmi/id/product_version", "N/A");
    info.board_vendor = read_file("/sys/class/dmi/id/board_vendor", "N/A");
    info.board_name = read_file("/sys/class/dmi/id/board_name", "N/A");
    info.bios_vendor = read_file("/sys/class/dmi/id/bios_vendor", "N/A");
    info.bios_version = read_file("/sys/class/dmi/id/bios_version", "N/A");
    info.bios_date = read_file("/sys/class/dmi/id/bios_date", "N/A");
    
    // CPU информация
    struct utsname uname_info;
    if (uname(&uname_info) == 0) {
        info.cpu_model = uname_info.machine;
    }
    
    // Память через /proc/meminfo
    std::ifstream meminfo("/proc/meminfo");
    if (meminfo.is_open()) {
        std::string line;
        while (std::getline(meminfo, line)) {
            if (line.find("MemTotal:") == 0) {
                std::istringstream iss(line);
                std::string label;
                long long mem_kb;
                iss >> label >> mem_kb;
                double mem_gb = mem_kb / (1024.0 * 1024.0);
                std::ostringstream oss;
                oss << mem_gb << " GB";
                info.total_memory = oss.str();
                break;
            }
        }
        meminfo.close();
    } else {
        info.total_memory = "N/A";
    }
    
    return info;
}

OSInfo SystemInfoLib::get_os_info() {
    OSInfo info;
    
    struct utsname uname_info;
    if (uname(&uname_info) == 0) {
        info.system = uname_info.sysname;
        info.release = uname_info.release;
        info.version = uname_info.version;
        info.machine = uname_info.machine;
        info.hostname = uname_info.nodename;
        info.kernel_version = uname_info.release;
    }
    
    // Дистрибутив из /etc/os-release
    std::ifstream os_release("/etc/os-release");
    if (os_release.is_open()) {
        std::string line;
        while (std::getline(os_release, line)) {
            if (line.find("PRETTY_NAME=") == 0) {
                size_t start = line.find('"');
                size_t end = line.rfind('"');
                if (start != std::string::npos && end != std::string::npos && start < end) {
                    info.distribution = line.substr(start + 1, end - start - 1);
                }
                break;
            }
        }
        os_release.close();
    } else {
        info.distribution = "N/A";
    }
    
    return info;
}

EnvironmentInfo SystemInfoLib::get_environment_info() {
    EnvironmentInfo info;
    
    // Десктопное окружение из переменных окружения
    const char* de = std::getenv("XDG_CURRENT_DESKTOP");
    info.desktop_environment = de ? de : "N/A";
    
    const char* ds = std::getenv("XDG_SESSION_TYPE");
    info.display_server = ds ? ds : "N/A";
    
    const char* shell = std::getenv("SHELL");
    info.shell = shell ? shell : "N/A";
    
    // Window manager через процессы
    if (info.desktop_environment == "N/A") {
        FILE* pipe = popen("ps -e", "r");
        if (pipe) {
            char buffer[128];
            std::string output;
            while (fgets(buffer, sizeof(buffer), pipe) != nullptr) {
                output += buffer;
            }
            pclose(pipe);
            
            std::string lower_output = output;
            for (auto& c : lower_output) {
                c = std::tolower(c);
            }
            
            if (lower_output.find("gnome") != std::string::npos) {
                info.desktop_environment = "GNOME";
            } else if (lower_output.find("kde") != std::string::npos) {
                info.desktop_environment = "KDE";
            } else if (lower_output.find("xfce") != std::string::npos) {
                info.desktop_environment = "XFCE";
            } else if (lower_output.find("mate") != std::string::npos) {
                info.desktop_environment = "MATE";
            }
        }
    }
    
    // Window manager
    FILE* wm_pipe = popen("ps aux | grep -i 'window_manager\\|i3\\|openbox\\|compiz'", "r");
    if (wm_pipe) {
        char buffer[128];
        std::string output;
        while (fgets(buffer, sizeof(buffer), wm_pipe) != nullptr) {
            output += buffer;
        }
        pclose(wm_pipe);
        
        if (output.find("i3") != std::string::npos) {
            info.window_manager = "i3";
        } else if (output.find("openbox") != std::string::npos) {
            info.window_manager = "Openbox";
        } else if (output.find("compiz") != std::string::npos) {
            info.window_manager = "Compiz";
        } else {
            info.window_manager = info.desktop_environment;
        }
    } else {
        info.window_manager = "N/A";
    }
    
    return info;
}

std::vector<BootloaderInfo> SystemInfoLib::get_bootloaders() {
    std::vector<BootloaderInfo> bootloaders;
    
    // Проверяем GRUB
    if (file_exists("/boot/grub/grub.cfg") || file_exists("/boot/grub2/grub.cfg")) {
        BootloaderInfo grub;
        grub.name = "GRUB";
        grub.path = file_exists("/boot/grub/grub.cfg") ? "/boot/grub/grub.cfg" : "/boot/grub2/grub.cfg";
        grub.active = true;
        bootloaders.push_back(grub);
    }
    
    // Проверяем systemd-boot
    if (file_exists("/boot/loader/loader.conf")) {
        BootloaderInfo systemd;
        systemd.name = "systemd-boot";
        systemd.path = "/boot/loader/loader.conf";
        systemd.active = true;
        bootloaders.push_back(systemd);
    }
    
    // Проверяем rEFInd
    if (file_exists("/boot/refind/refind.conf")) {
        BootloaderInfo refind;
        refind.name = "rEFInd";
        refind.path = "/boot/refind/refind.conf";
        refind.active = true;
        bootloaders.push_back(refind);
    }
    
    // Проверяем Windows Boot Manager через efibootmgr
    FILE* pipe = popen("efibootmgr 2>/dev/null", "r");
    if (pipe) {
        char buffer[512];
        std::string output;
        while (fgets(buffer, sizeof(buffer), pipe) != nullptr) {
            output += buffer;
        }
        pclose(pipe);
        
        if (output.find("Windows Boot Manager") != std::string::npos) {
            BootloaderInfo windows;
            windows.name = "Windows Boot Manager";
            windows.path = "EFI";
            windows.active = false;
            bootloaders.push_back(windows);
        }
    }
    
    return bootloaders;
}

std::vector<std::string> SystemInfoLib::get_installed_os() {
    std::vector<std::string> os_list;
    
    // Текущая ОС из /etc/os-release
    if (file_exists("/etc/os-release")) {
        std::ifstream os_release("/etc/os-release");
        std::string line;
        while (std::getline(os_release, line)) {
            if (line.find("PRETTY_NAME=") == 0) {
                size_t start = line.find('"');
                size_t end = line.rfind('"');
                if (start != std::string::npos && end != std::string::npos && start < end) {
                    os_list.push_back(line.substr(start + 1, end - start - 1) + " (Current)");
                }
                break;
            }
        }
        os_release.close();
    }
    
    // Проверяем GRUB конфигурацию
    if (file_exists("/boot/grub/grub.cfg")) {
        std::ifstream grub_cfg("/boot/grub/grub.cfg");
        std::string line;
        while (std::getline(grub_cfg, line)) {
            size_t pos = line.find("menuentry");
            if (pos != std::string::npos) {
                size_t start = line.find('"', pos);
                size_t end = line.find('"', start + 1);
                if (start != std::string::npos && end != std::string::npos) {
                    os_list.push_back(line.substr(start + 1, end - start - 1) + " (GRUB)");
                }
            }
        }
        grub_cfg.close();
    }
    
    // Проверяем Windows через /mnt
    DIR* dir = opendir("/mnt");
    if (dir) {
        struct dirent* entry;
        while ((entry = readdir(dir)) != nullptr) {
            std::string path = "/mnt/" + std::string(entry->d_name);
            if (file_exists(path + "/Windows") || file_exists(path + "/Program Files")) {
                os_list.push_back("Windows (Detected)");
                break;
            }
        }
        closedir(dir);
    }
    
    return os_list;
}

std::map<std::string, std::string> SystemInfoLib::get_bios_info() {
    std::map<std::string, std::string> bios;
    
    bios["vendor"] = read_file("/sys/class/dmi/id/bios_vendor", "N/A");
    bios["version"] = read_file("/sys/class/dmi/id/bios_version", "N/A");
    bios["release_date"] = read_file("/sys/class/dmi/id/bios_date", "N/A");
    bios["revision"] = read_file("/sys/class/dmi/id/bios_revision", "N/A");
    
    return bios;
}

std::vector<std::string> SystemInfoLib::get_drivers() {
    std::vector<std::string> drivers;
    
    // Получаем загруженные модули ядра
    FILE* pipe = popen("lsmod", "r");
    if (pipe) {
        char buffer[256];
        bool first_line = true;
        while (fgets(buffer, sizeof(buffer), pipe) != nullptr) {
            if (first_line) {
                first_line = false;
                continue; // Пропускаем заголовок
            }
            std::string line(buffer);
            size_t space_pos = line.find(' ');
            if (space_pos != std::string::npos) {
                drivers.push_back(line.substr(0, space_pos));
            }
        }
        pclose(pipe);
    }
    
    return drivers;
}

std::string SystemInfoLib::get_serial_number() {
    return read_file("/sys/class/dmi/id/product_serial", "N/A");
}

} // namespace SystemInfo
