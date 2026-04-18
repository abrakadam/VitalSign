#include "keyboard_analyzer.h"
#include <fstream>
#include <sstream>
#include <iostream>
#include <algorithm>
#include <filesystem>
#include <cstdio>

namespace fs = std::filesystem;

// ==================== Получение списка клавиатур ====================
std::vector<KeyboardAnalyzer::KeyboardInfo> KeyboardAnalyzer::get_keyboards() {
    std::vector<KeyboardInfo> keyboards;
    
    try {
        // Читаем из /proc/bus/input/devices
        std::ifstream input_file("/proc/bus/input/devices");
        if (input_file.is_open()) {
            std::string line;
            KeyboardInfo current_keyboard;
            bool in_keyboard = false;
            
            while (std::getline(input_file, line)) {
                if (line.empty()) {
                    if (in_keyboard && !current_keyboard.name.empty()) {
                        current_keyboard.is_internal = is_internal_keyboard(current_keyboard);
                        current_keyboard.type = current_keyboard.is_internal ? "internal" : "external";
                        keyboards.push_back(current_keyboard);
                    }
                    current_keyboard = KeyboardInfo();
                    in_keyboard = false;
                    continue;
                }
                
                if (line.find("N: Name=") == 0) {
                    current_keyboard.name = line.substr(8);
                    if (current_keyboard.name.front() == '"' && current_keyboard.name.back() == '"') {
                        current_keyboard.name = current_keyboard.name.substr(1, current_keyboard.name.length() - 2);
                    }
                    in_keyboard = true;
                    
                    // Проверяем, это ли клавиатура
                    std::string name_lower = current_keyboard.name;
                    std::transform(name_lower.begin(), name_lower.end(), name_lower.begin(), ::tolower);
                    if (name_lower.find("keyboard") == std::string::npos && 
                        name_lower.find("keypad") == std::string::npos) {
                        in_keyboard = false;
                        continue;
                    }
                    
                    current_keyboard.status = "connected";
                }
                
                if (line.find("B: BUS=") == 0) {
                    current_keyboard.bus = line.substr(7);
                }
                
                if (line.find("P: Vendor=") == 0) {
                    current_keyboard.manufacturer = line.substr(11);
                }
                
                if (line.find("P: Product=") == 0) {
                    current_keyboard.product = line.substr(12);
                }
            }
            
            // Добавляем последнюю клавиатуру
            if (in_keyboard && !current_keyboard.name.empty()) {
                current_keyboard.is_internal = is_internal_keyboard(current_keyboard);
                current_keyboard.type = current_keyboard.is_internal ? "internal" : "external";
                keyboards.push_back(current_keyboard);
            }
            
            input_file.close();
        }
    } catch (const std::exception& e) {
        std::cerr << "Error reading keyboards: " << e.what() << std::endl;
    }
    
    return keyboards;
}

// ==================== Проверка встроенная ли клавиатура ====================
bool KeyboardAnalyzer::is_internal_keyboard(const KeyboardInfo& keyboard) {
    std::string name_lower = keyboard.name;
    std::transform(name_lower.begin(), name_lower.end(), name_lower.begin(), ::tolower);
    
    // Встроенная клавиатура ноутбука
    if (name_lower.find("at keyboard") != std::string::npos ||
        name_lower.find("system keyboard") != std::string::npos ||
        name_lower.find("internal") != std::string::npos ||
        name_lower.find("laptop") != std::string::npos ||
        name_lower.find("notebook") != std::string::npos) {
        return true;
    }
    
    // PS/2 клавиатура обычно встроенная
    if (keyboard.bus.find("0011") != std::string::npos) { // PS/2
        return true;
    }
    
    return false;
}

// ==================== Проверка здоровья клавиатуры ====================
KeyboardAnalyzer::KeyboardHealth KeyboardAnalyzer::check_keyboard_health(const KeyboardInfo& keyboard) {
    KeyboardHealth health;
    health.is_healthy = true;
    health.health_score = 100;
    health.total_keys = 104; // Стандартная клавиатура
    health.working_keys = 104;
    health.broken_keys = 0;
    
    // Обнаруживаем проблемы
    health.issues = detect_keyboard_issues(keyboard);
    
    // Вычисляем оценку здоровья
    health.health_score = calculate_health_score(keyboard, health.issues);
    
    // Определяем общее состояние
    if (health.health_score >= 80) {
        health.is_healthy = true;
    } else if (health.health_score >= 60) {
        health.is_healthy = true;
    } else {
        health.is_healthy = false;
    }
    
    return health;
}

// ==================== Обнаружение клавиш ====================
std::vector<KeyboardAnalyzer::KeyInfo> KeyboardAnalyzer::detect_keys(const KeyboardInfo& keyboard) {
    std::vector<KeyInfo> keys;
    
    // Список стандартных клавиш
    std::vector<std::string> standard_keys = {
        "ESC", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
        "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=",
        "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", "\\",
        "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'",
        "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/",
        "SPACE", "TAB", "CAPS", "SHIFT_L", "SHIFT_R", "CTRL_L", "CTRL_R",
        "ALT_L", "ALT_R", "META_L", "META_R",
        "ENTER", "BACKSPACE", "DELETE", "INSERT", "HOME", "END", "PAGE_UP", "PAGE_DOWN",
        "UP", "DOWN", "LEFT", "RIGHT"
    };
    
    for (const auto& key_name : standard_keys) {
        KeyInfo key;
        key.key_name = key_name;
        key.key_code = "";
        key.works = true;  // По умолчанию считаем работающими
        key.detected = true;
        keys.push_back(key);
    }
    
    return keys;
}

// ==================== Обнаружение проблем с клавиатурой ====================
std::vector<std::string> KeyboardAnalyzer::detect_keyboard_issues(const KeyboardInfo& keyboard) {
    std::vector<std::string> issues;
    
    // Проверка производителя
    if (keyboard.manufacturer.empty()) {
        issues.push_back("Manufacturer information not available");
    }
    
    // Проверка продукта
    if (keyboard.product.empty()) {
        issues.push_back("Product information not available");
    }
    
    // Проверка статуса
    if (keyboard.status.empty() || keyboard.status == "disconnected") {
        issues.push_back("Keyboard not connected");
    }
    
    // Проверка типа подключения
    if (keyboard.bus.empty()) {
        issues.push_back("Bus type not detected");
    }
    
    // Если это встроенная клавиатура, проверяем дополнительные параметры
    if (keyboard.is_internal) {
        // Встроенная клавиатура должна быть всегда подключена
        if (keyboard.status != "connected") {
            issues.push_back("Internal keyboard disconnected");
        }
    }
    
    return issues;
}

// ==================== Вычисление оценки здоровья ====================
int KeyboardAnalyzer::calculate_health_score(const KeyboardInfo& keyboard, const std::vector<std::string>& issues) {
    int score = 100;
    
    // Вычитаем баллы за каждую проблему
    for (const auto& issue : issues) {
        if (issue.find("not connected") != std::string::npos) {
            score -= 50;
        } else if (issue.find("Manufacturer") != std::string::npos) {
            score -= 10;
        } else if (issue.find("Product") != std::string::npos) {
            score -= 10;
        } else if (issue.find("Bus type") != std::string::npos) {
            score -= 15;
        } else if (issue.find("Internal keyboard") != std::string::npos) {
            score -= 30;
        } else {
            score -= 10;
        }
    }
    
    return std::max(0, score);
}
