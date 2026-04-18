#include "device_analyzer.h"
#include <fstream>
#include <sstream>
#include <iostream>
#include <algorithm>
#include <filesystem>
#include <cstdio>

namespace fs = std::filesystem;

// ==================== USB Устройства ====================
std::vector<DeviceAnalyzer::USBDeviceInfo> DeviceAnalyzer::get_usb_devices() {
    std::vector<USBDeviceInfo> devices;
    try {
        std::string usb_path = "/sys/bus/usb/devices/";
        for (const auto& entry : fs::directory_iterator(usb_path)) {
            std::string path = entry.path().string();
            std::string filename = entry.path().filename().string();
            if (filename.find(":") == std::string::npos) continue;
            
            USBDeviceInfo info;
            info.bus = filename.substr(0, filename.find(":"));
            info.device = filename.substr(filename.find(":") + 1);
            info.power_ma = 0;
            info.status = "connected";
            
            std::ifstream vendor_file(path + "/manufacturer");
            if (vendor_file.is_open()) { std::getline(vendor_file, info.vendor); vendor_file.close(); }
            
            std::ifstream product_file(path + "/product");
            if (product_file.is_open()) { std::getline(product_file, info.product); product_file.close(); }
            
            std::ifstream serial_file(path + "/serial");
            if (serial_file.is_open()) { std::getline(serial_file, info.serial); serial_file.close(); }
            
            std::ifstream power_file(path + "/bMaxPower");
            if (power_file.is_open()) { 
                std::string power_str; std::getline(power_file, power_str); 
                info.power_ma = std::stoi(power_str); power_file.close(); 
            }
            
            if (!info.vendor.empty() || !info.product.empty()) devices.push_back(info);
        }
    } catch (const std::exception& e) { std::cerr << "Error: " << e.what() << std::endl; }
    return devices;
}

std::string DeviceAnalyzer::get_usb_device_type(const USBDeviceInfo& device) {
    std::string product_lower = device.product;
    std::transform(product_lower.begin(), product_lower.end(), product_lower.begin(), ::tolower);
    
    if (product_lower.find("flash") != std::string::npos || product_lower.find("storage") != std::string::npos) return "flash_drive";
    if (product_lower.find("headphone") != std::string::npos || product_lower.find("audio") != std::string::npos) return "audio_device";
    if (product_lower.find("keyboard") != std::string::npos) return "keyboard";
    if (product_lower.find("mouse") != std::string::npos) return "mouse";
    if (product_lower.find("camera") != std::string::npos || product_lower.find("webcam") != std::string::npos) return "camera";
    if (product_lower.find("ethernet") != std::string::npos || product_lower.find("network") != std::string::npos) return "network_adapter";
    return "unknown";
}

// ==================== Батарея и зарядка ====================
DeviceAnalyzer::BatteryInfo DeviceAnalyzer::get_battery_info() {
    BatteryInfo info;
    info.is_present = false;
    info.is_charging = false;
    info.percentage = 0;
    info.voltage_mv = 0;
    info.current_ma = 0;
    info.power_mw = 0;
    
    try {
        std::string battery_path = "/sys/class/power_supply/";
        for (const auto& entry : fs::directory_iterator(battery_path)) {
            std::string path = entry.path().string();
            std::string name = entry.path().filename().string();
            if (name.find("BAT") != 0) continue;
            
            info.is_present = true;
            
            std::ifstream status_file(path + "/status");
            if (status_file.is_open()) { 
                std::getline(status_file, info.status);
                info.is_charging = (info.status == "Charging");
                status_file.close();
            }
            
            std::ifstream capacity_file(path + "/capacity");
            if (capacity_file.is_open()) { 
                std::string cap; std::getline(capacity_file, cap);
                info.percentage = std::stoi(cap); capacity_file.close();
            }
            
            std::ifstream voltage_file(path + "/voltage_now");
            if (voltage_file.is_open()) { 
                std::string volt; std::getline(voltage_file, volt);
                info.voltage_mv = std::stoi(volt) / 1000; voltage_file.close();
            }
            
            std::ifstream current_file(path + "/current_now");
            if (current_file.is_open()) { 
                std::string curr; std::getline(current_file, curr);
                info.current_ma = std::stoi(curr) / 1000; current_file.close();
            }
            
            if (info.voltage_mv > 0 && info.current_ma > 0) {
                info.power_mw = (info.voltage_mv * info.current_ma) / 1000;
            }
            
            std::ifstream manufacturer_file(path + "/manufacturer");
            if (manufacturer_file.is_open()) { std::getline(manufacturer_file, info.manufacturer); manufacturer_file.close(); }
            
            std::ifstream model_file(path + "/model_name");
            if (model_file.is_open()) { std::getline(model_file, info.model); model_file.close(); }
            
            std::ifstream tech_file(path + "/technology");
            if (tech_file.is_open()) { std::getline(tech_file, info.technology); tech_file.close(); }
            
            break;
        }
    } catch (const std::exception& e) { std::cerr << "Error: " << e.what() << std::endl; }
    return info;
}

std::vector<std::string> DeviceAnalyzer::detect_battery_issues(const BatteryInfo& info) {
    std::vector<std::string> issues;
    if (!info.is_present) { issues.push_back("Батарея не обнаружена"); return issues; }
    if (info.percentage < 20 && !info.is_charging) issues.push_back("Низкий заряд батареи (< 20%)");
    if (info.voltage_mv > 0 && info.voltage_mv < 10000) issues.push_back("Низкое напряжение (возможен износ)");
    if (info.current_ma > 0 && info.is_charging && info.current_ma < 500) issues.push_back("Медленная зарядка (< 500 мА)");
    if (info.technology.empty()) issues.push_back("Не удалось определить технологию батареи");
    return issues;
}

// ==================== Аудио устройства ====================
std::vector<DeviceAnalyzer::AudioDeviceInfo> DeviceAnalyzer::get_audio_devices() {
    std::vector<AudioDeviceInfo> devices;
    try {
        FILE* pipe = popen("aplay -l", "r");
        if (pipe) {
            char buffer[256];
            while (fgets(buffer, sizeof(buffer), pipe) != nullptr) {
                std::string line(buffer);
                if (line.find("card") != std::string::npos) {
                    AudioDeviceInfo info;
                    size_t card_pos = line.find("card ");
                    if (card_pos != std::string::npos) {
                        size_t colon_pos = line.find(":", card_pos);
                        info.card = line.substr(card_pos + 5, colon_pos - card_pos - 5);
                        size_t device_pos = line.find("device ");
                        if (device_pos != std::string::npos) {
                            size_t colon2_pos = line.find(":", device_pos);
                            info.device = line.substr(device_pos + 7, colon2_pos - device_pos - 7);
                        }
                        size_t colon3_pos = line.find(": ", colon_pos + 2);
                        if (colon3_pos != std::string::npos) {
                            info.name = line.substr(colon3_pos + 2);
                            if (!info.name.empty() && info.name.back() == '\n') info.name.pop_back();
                        }
                        
                        std::string name_lower = info.name;
                        std::transform(name_lower.begin(), name_lower.end(), name_lower.begin(), ::tolower);
                        if (name_lower.find("headphone") != std::string::npos || name_lower.find("headset") != std::string::npos) info.type = "headphones";
                        else if (name_lower.find("microphone") != std::string::npos) info.type = "microphone";
                        else if (name_lower.find("speaker") != std::string::npos) info.type = "speakers";
                        else info.type = "unknown";
                        info.status = "connected";
                        devices.push_back(info);
                    }
                }
            }
            pclose(pipe);
        }
    } catch (const std::exception& e) { std::cerr << "Error: " << e.what() << std::endl; }
    return devices;
}

std::vector<std::string> DeviceAnalyzer::detect_audio_issues(const AudioDeviceInfo& device) {
    std::vector<std::string> issues;
    if (device.name.empty()) issues.push_back("Не удалось определить имя устройства");
    if (device.type == "unknown") issues.push_back("Неизвестный тип аудиоустройства");
    return issues;
}

// ==================== Ввод (клавиатура, мышь) ====================
std::vector<DeviceAnalyzer::InputDeviceInfo> DeviceAnalyzer::get_input_devices() {
    std::vector<InputDeviceInfo> devices;
    try {
        std::ifstream input_file("/proc/bus/input/devices");
        if (input_file.is_open()) {
            std::string line;
            InputDeviceInfo current_device;
            bool in_device = false;
            while (std::getline(input_file, line)) {
                if (line.empty()) {
                    if (in_device && !current_device.name.empty()) {
                        current_device.is_connected = true;
                        current_device.status = "connected";
                        devices.push_back(current_device);
                    }
                    current_device = InputDeviceInfo();
                    in_device = false;
                    continue;
                }
                if (line.find("N: Name=") == 0) {
                    current_device.name = line.substr(8);
                    if (current_device.name.front() == '"' && current_device.name.back() == '"') {
                        current_device.name = current_device.name.substr(1, current_device.name.length() - 2);
                    }
                    in_device = true;
                    std::string name_lower = current_device.name;
                    std::transform(name_lower.begin(), name_lower.end(), name_lower.begin(), ::tolower);
                    if (name_lower.find("keyboard") != std::string::npos) current_device.type = "keyboard";
                    else if (name_lower.find("mouse") != std::string::npos) current_device.type = "mouse";
                    else if (name_lower.find("touchpad") != std::string::npos) current_device.type = "touchpad";
                    else current_device.type = "unknown";
                }
                if (line.find("B: BUS=") == 0) current_device.bus = line.substr(7);
                if (line.find("P: Vendor=") == 0) current_device.vendor = line.substr(11);
                if (line.find("P: Product=") == 0) current_device.product = line.substr(12);
            }
            if (in_device && !current_device.name.empty()) {
                current_device.is_connected = true;
                current_device.status = "connected";
                devices.push_back(current_device);
            }
            input_file.close();
        }
    } catch (const std::exception& e) { std::cerr << "Error: " << e.what() << std::endl; }
    return devices;
}

std::vector<std::string> DeviceAnalyzer::detect_input_issues(const InputDeviceInfo& device) {
    std::vector<std::string> issues;
    if (device.type == "unknown") issues.push_back("Неизвестный тип устройства ввода");
    if (device.vendor.empty()) issues.push_back("Не удалось определить производителя");
    return issues;
}

// ==================== Гнезда ноутбука ====================
DeviceAnalyzer::PortInfo DeviceAnalyzer::get_port_info() {
    PortInfo info;
    info.is_laptop = false;
    info.has_hdmi = false;
    info.has_usb_c = false;
    info.has_usb_a = false;
    info.has_ethernet = false;
    info.has_audio_jack = false;
    info.has_sd_card = false;
    info.chassis_type = "unknown";
    
    try {
        std::ifstream dmi_file("/sys/class/dmi/id/chassis_type");
        if (dmi_file.is_open()) {
            std::string chassis_str;
            std::getline(dmi_file, chassis_str);
            int chassis_type = std::stoi(chassis_str);
            if (chassis_type >= 8 && chassis_type <= 10 || chassis_type == 14) {
                info.is_laptop = true;
                info.chassis_type = "laptop";
            } else if (chassis_type >= 3 && chassis_type <= 7) {
                info.chassis_type = "desktop";
            }
            dmi_file.close();
        }
        
        FILE* pipe = popen("lspci", "r");
        if (pipe) {
            char buffer[256];
            while (fgets(buffer, sizeof(buffer), pipe) != nullptr) {
                std::string line(buffer);
                std::transform(line.begin(), line.end(), line.begin(), ::tolower);
                if (line.find("hdmi") != std::string::npos) info.has_hdmi = true;
                if (line.find("ethernet") != std::string::npos || line.find("network") != std::string::npos) info.has_ethernet = true;
            }
            pclose(pipe);
        }
        
        for (const auto& entry : fs::directory_iterator("/sys/bus/usb/devices/")) {
            std::string filename = entry.path().filename().string();
            if (filename.find("usb") == 0) {
                info.has_usb_a = true;
                std::ifstream speed_file(entry.path().string() + "/speed");
                if (speed_file.is_open()) {
                    std::string speed; std::getline(speed_file, speed);
                    if (speed.find("10000") != std::string::npos || speed.find("5000") != std::string::npos) {
                        info.has_usb_c = true;
                    }
                    speed_file.close();
                }
            }
        }
        
        info.has_audio_jack = true; // По умолчанию для большинства систем
        
    } catch (const std::exception& e) { std::cerr << "Error: " << e.what() << std::endl; }
    return info;
}
