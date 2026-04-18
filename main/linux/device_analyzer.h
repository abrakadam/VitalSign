#ifndef DEVICE_ANALYZER_H
#define DEVICE_ANALYZER_H

#include <string>
#include <vector>
#include <map>

class DeviceAnalyzer {
public:
    struct USBDeviceInfo {
        std::string vendor;
        std::string product;
        std::string serial;
        std::string bus;
        std::string device;
        int power_ma;
        std::string status;
    };

    struct BatteryInfo {
        bool is_present;
        bool is_charging;
        int percentage;
        int voltage_mv;
        int current_ma;
        int power_mw;
        std::string manufacturer;
        std::string model;
        std::string technology;
        std::string status;
    };

    struct AudioDeviceInfo {
        std::string name;
        std::string type;
        std::string status;
        std::string card;
        std::string device;
    };

    struct InputDeviceInfo {
        std::string name;
        std::string type;
        std::string bus;
        std::string vendor;
        std::string product;
        bool is_connected;
        std::string status;
    };

    struct PortInfo {
        bool is_laptop;
        bool has_hdmi;
        bool has_usb_c;
        bool has_usb_a;
        bool has_ethernet;
        bool has_audio_jack;
        bool has_sd_card;
        std::string chassis_type;
    };

    static std::vector<USBDeviceInfo> get_usb_devices();
    static std::string get_usb_device_type(const USBDeviceInfo& device);
    static BatteryInfo get_battery_info();
    static std::vector<std::string> detect_battery_issues(const BatteryInfo& info);
    static std::vector<AudioDeviceInfo> get_audio_devices();
    static std::vector<std::string> detect_audio_issues(const AudioDeviceInfo& device);
    static std::vector<InputDeviceInfo> get_input_devices();
    static std::vector<std::string> detect_input_issues(const InputDeviceInfo& device);
    static PortInfo get_port_info();
};

#endif
