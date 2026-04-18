#ifndef KEYBOARD_ANALYZER_H
#define KEYBOARD_ANALYZER_H

#include <string>
#include <vector>
#include <map>

class KeyboardAnalyzer {
public:
    struct KeyboardInfo {
        std::string name;
        std::string manufacturer;
        std::string product;
        std::string bus;        // usb, ps2, etc.
        std::string type;       // internal, external
        bool is_internal;
        std::string interface;
        std::string status;
    };

    struct KeyInfo {
        std::string key_name;
        std::string key_code;
        bool works;
        bool detected;
    };

    struct KeyboardHealth {
        bool is_healthy;
        std::vector<std::string> issues;
        int health_score;
        int total_keys;
        int working_keys;
        int broken_keys;
    };

    static std::vector<KeyboardInfo> get_keyboards();
    static bool is_internal_keyboard(const KeyboardInfo& keyboard);
    static KeyboardHealth check_keyboard_health(const KeyboardInfo& keyboard);
    static std::vector<KeyInfo> detect_keys(const KeyboardInfo& keyboard);
    static std::vector<std::string> detect_keyboard_issues(const KeyboardInfo& keyboard);
    static int calculate_health_score(const KeyboardInfo& keyboard, const std::vector<std::string>& issues);
};

#endif
