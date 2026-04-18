#include "config_manager.h"
#include <filesystem>
#include <iostream>
#include <algorithm>

namespace fs = std::filesystem;

std::string ConfigManager::config_dir = "";
std::string ConfigManager::config_file = "";

// ==================== Получение директории конфигурации ====================
std::string ConfigManager::get_config_dir() {
    if (!config_dir.empty()) {
        return config_dir;
    }
    
#ifdef _WIN32
    // Windows: используем APPDATA или USERPROFILE
    const char* appdata = std::getenv("APPDATA");
    const char* userprofile = std::getenv("USERPROFILE");
    
    if (appdata) {
        config_dir = std::string(appdata) + "\\VitalSign";
    } else if (userprofile) {
        config_dir = std::string(userprofile) + "\\AppData\\Roaming\\VitalSign";
    } else {
        // Fallback на текущую директорию
        config_dir = ".VitalSign";
    }
#else
    // Linux/Mac: используем HOME
    const char* home = std::getenv("HOME");
    if (home) {
        config_dir = std::string(home) + "/.VitalSign";
    } else {
        // Fallback на текущую директорию
        config_dir = ".VitalSign";
    }
#endif
    
    return config_dir;
}

// ==================== Создание директории конфигурации ====================
bool ConfigManager::create_config_dir() {
    std::string dir = get_config_dir();
    
    try {
        if (!fs::exists(dir)) {
            fs::create_directory(dir);
            std::cout << "Config directory created: " << dir << std::endl;
            return true;
        } else {
            std::cout << "Config directory already exists: " << dir << std::endl;
            return true;
        }
    } catch (const std::exception& e) {
        std::cerr << "Error creating config directory: " << e.what() << std::endl;
        return false;
    }
}

// ==================== Сохранение конфигурации ====================
bool ConfigManager::save_config(const std::string& key, const std::string& value) {
    std::string dir = get_config_dir();
    config_file = dir + "/config.ini";
    
    try {
        // Загружаем существующие конфигурации
        std::map<std::string, std::string> configs = load_all_configs();
        
        // Обновляем значение
        configs[key] = value;
        
        // Сохраняем все конфигурации
        return save_all_configs(configs);
    } catch (const std::exception& e) {
        std::cerr << "Error saving config: " << e.what() << std::endl;
        return false;
    }
}

// ==================== Загрузка конфигурации ====================
std::string ConfigManager::load_config(const std::string& key) {
    std::string dir = get_config_dir();
    config_file = dir + "/config.ini";
    
    try {
        std::map<std::string, std::string> configs = load_all_configs();
        auto it = configs.find(key);
        if (it != configs.end()) {
            return it->second;
        }
    } catch (const std::exception& e) {
        std::cerr << "Error loading config: " << e.what() << std::endl;
    }
    
    return "";
}

// ==================== Удаление конфигурации ====================
bool ConfigManager::delete_config(const std::string& key) {
    std::string dir = get_config_dir();
    config_file = dir + "/config.ini";
    
    try {
        std::map<std::string, std::string> configs = load_all_configs();
        auto it = configs.find(key);
        if (it != configs.end()) {
            configs.erase(it);
            return save_all_configs(configs);
        }
    } catch (const std::exception& e) {
        std::cerr << "Error deleting config: " << e.what() << std::endl;
    }
    
    return false;
}

// ==================== Загрузка всех конфигураций ====================
std::map<std::string, std::string> ConfigManager::load_all_configs() {
    std::map<std::string, std::string> configs;
    std::string dir = get_config_dir();
    config_file = dir + "/config.ini";
    
    try {
        if (!fs::exists(config_file)) {
            return configs;
        }
        
        std::ifstream file(config_file);
        if (!file.is_open()) {
            return configs;
        }
        
        std::string line;
        while (std::getline(file, line)) {
            // Пропускаем комментарии и пустые строки
            if (line.empty() || line[0] == '#' || line[0] == ';') {
                continue;
            }
            
            // Парсим key=value
            size_t pos = line.find('=');
            if (pos != std::string::npos) {
                std::string key = line.substr(0, pos);
                std::string value = line.substr(pos + 1);
                
                // Убираем пробелы
                key.erase(0, key.find_first_not_of(" \t"));
                key.erase(key.find_last_not_of(" \t") + 1);
                value.erase(0, value.find_first_not_of(" \t"));
                value.erase(value.find_last_not_of(" \t") + 1);
                
                configs[key] = value;
            }
        }
        
        file.close();
    } catch (const std::exception& e) {
        std::cerr << "Error loading all configs: " << e.what() << std::endl;
    }
    
    return configs;
}

// ==================== Сохранение всех конфигураций ====================
bool ConfigManager::save_all_configs(const std::map<std::string, std::string>& configs) {
    std::string dir = get_config_dir();
    config_file = dir + "/config.ini";
    
    try {
        // Убеждаемся что директория существует
        if (!fs::exists(dir)) {
            fs::create_directory(dir);
        }
        
        std::ofstream file(config_file);
        if (!file.is_open()) {
            std::cerr << "Error opening config file for writing" << std::endl;
            return false;
        }
        
        // Записываем заголовок
        file << "# VitalSign Configuration File\n";
        file << "# Generated by VitalSign\n\n";
        
        // Записываем все конфигурации
        for (const auto& config : configs) {
            file << config.first << "=" << config.second << "\n";
        }
        
        file.close();
        return true;
    } catch (const std::exception& e) {
        std::cerr << "Error saving all configs: " << e.what() << std::endl;
        return false;
    }
}

// ==================== Очистка конфигурации ====================
bool ConfigManager::clear_config() {
    std::string dir = get_config_dir();
    config_file = dir + "/config.ini";
    
    try {
        if (fs::exists(config_file)) {
            fs::remove(config_file);
            return true;
        }
    } catch (const std::exception& e) {
        std::cerr << "Error clearing config: " << e.what() << std::endl;
    }
    
    return false;
}

// ==================== Получение пути к локализациям ====================
std::string ConfigManager::get_locale_path() {
    std::string dir = get_config_dir();
    return dir + "/locales/";
}

// ==================== Сохранение данных локализации ====================
bool ConfigManager::save_locale_data(const std::string& language, const std::string& data) {
    std::string dir = get_config_dir();
    std::string locale_dir = dir + "/locales/";
    
    try {
        // Создаем директорию для локализаций
        if (!fs::exists(locale_dir)) {
            fs::create_directory(locale_dir);
        }
        
        std::string locale_file = locale_dir + language + ".json";
        std::ofstream file(locale_file);
        if (!file.is_open()) {
            std::cerr << "Error opening locale file for writing" << std::endl;
            return false;
        }
        
        file << data;
        file.close();
        return true;
    } catch (const std::exception& e) {
        std::cerr << "Error saving locale data: " << e.what() << std::endl;
        return false;
    }
}

// ==================== Загрузка данных локализации ====================
std::string ConfigManager::load_locale_data(const std::string& language) {
    std::string dir = get_config_dir();
    std::string locale_dir = dir + "/locales/";
    std::string locale_file = locale_dir + language + ".json";
    
    try {
        if (!fs::exists(locale_file)) {
            return "";
        }
        
        std::ifstream file(locale_file);
        if (!file.is_open()) {
            return "";
        }
        
        std::stringstream buffer;
        buffer << file.rdbuf();
        file.close();
        
        return buffer.str();
    } catch (const std::exception& e) {
        std::cerr << "Error loading locale data: " << e.what() << std::endl;
    }
    
    return "";
}

// ==================== Получение списка доступных локализаций ====================
std::vector<std::string> ConfigManager::get_available_locales() {
    std::vector<std::string> locales;
    std::string dir = get_config_dir();
    std::string locale_dir = dir + "/locales/";
    
    try {
        if (!fs::exists(locale_dir)) {
            return locales;
        }
        
        for (const auto& entry : fs::directory_iterator(locale_dir)) {
            if (entry.is_regular_file() && entry.path().extension() == ".json") {
                std::string filename = entry.path().stem().string();
                locales.push_back(filename);
            }
        }
    } catch (const std::exception& e) {
        std::cerr << "Error getting available locales: " << e.what() << std::endl;
    }
    
    return locales;
}
