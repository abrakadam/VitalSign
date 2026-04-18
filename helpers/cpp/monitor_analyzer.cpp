#include "monitor_analyzer.h"
#include <fstream>
#include <sstream>
#include <iostream>
#include <algorithm>
#include <filesystem>
#include <cstdio>

namespace fs = std::filesystem;

// ==================== Получение списка мониторов ====================
std::vector<MonitorAnalyzer::MonitorInfo> MonitorAnalyzer::get_monitors() {
    std::vector<MonitorInfo> monitors;
    
    try {
        // Используем xrandr для получения информации о мониторах (Linux)
        FILE* pipe = popen("xrandr", "r");
        if (pipe) {
            char buffer[256];
            std::string current_name;
            bool in_monitor = false;
            MonitorInfo current_monitor;
            
            while (fgets(buffer, sizeof(buffer), pipe) != nullptr) {
                std::string line(buffer);
                
                // Парсим вывод xrandr
                if (line.find(" connected") != std::string::npos) {
                    // Сохраняем предыдущий монитор если есть
                    if (in_monitor && !current_monitor.name.empty()) {
                        monitors.push_back(current_monitor);
                    }
                    
                    // Начинаем новый монитор
                    current_monitor = MonitorInfo();
                    in_monitor = true;
                    current_monitor.is_connected = true;
                    current_monitor.is_enabled = (line.find("connected primary") != std::string::npos || 
                                                   line.find(" connected ") != std::string::npos);
                    current_monitor.is_primary = (line.find("primary") != std::string::npos);
                    
                    // Получаем имя монитора
                    size_t space_pos = line.find(' ');
                    if (space_pos != std::string::npos) {
                        current_monitor.name = line.substr(0, space_pos);
                    }
                    
                    // Получаем разрешение и частоту
                    size_t connected_pos = line.find(" connected ");
                    if (connected_pos != std::string::npos) {
                        std::string rest = line.substr(connected_pos + 11);
                        
                        // Ищем разрешение (например, 1920x1080)
                        size_t x_pos = rest.find('x');
                        if (x_pos != std::string::npos) {
                            size_t start = x_pos - 1;
                            while (start > 0 && rest[start] != ' ') start--;
                            
                            size_t end = x_pos + 1;
                            while (end < rest.length() && rest[end] != ' ' && rest[end] != '+') end++;
                            
                            if (end < rest.length()) {
                                std::string resolution = rest.substr(start + 1, end - start - 1);
                                size_t res_x = resolution.find('x');
                                if (res_x != std::string::npos) {
                                    current_monitor.width = std::stoi(resolution.substr(0, res_x));
                                    current_monitor.height = std::stoi(resolution.substr(res_x + 1));
                                }
                            }
                        }
                    }
                    
                    // Получаем тип подключения
                    current_monitor.connection = get_connection_type(current_monitor.name);
                    
                    // Получаем EDID
                    current_monitor.edid = get_edid_info(current_monitor.name);
                    
                    // Извлекаем информацию из EDID
                    if (!current_monitor.edid.empty()) {
                        // Парсим EDID для получения производителя и модели
                        // Это упрощенная реализация
                        current_monitor.manufacturer = "Unknown";
                        current_monitor.model = current_monitor.name;
                        current_monitor.serial = "Unknown";
                    }
                    
                    current_monitor.status = current_monitor.is_enabled ? "Active" : "Connected but disabled";
                }
            }
            
            // Добавляем последний монитор
            if (in_monitor && !current_monitor.name.empty()) {
                monitors.push_back(current_monitor);
            }
            
            pclose(pipe);
        }
    } catch (const std::exception& e) {
        std::cerr << "Error reading monitors: " << e.what() << std::endl;
    }
    
    return monitors;
}

// ==================== Определение типа подключения ====================
std::string MonitorAnalyzer::get_connection_type(const std::string& port) {
    std::string port_lower = port;
    std::transform(port_lower.begin(), port_lower.end(), port_lower.begin(), ::tolower);
    
    if (port_lower.find("hdmi") != std::string::npos) {
        return "HDMI";
    } else if (port_lower.find("dp") != std::string::npos || port_lower.find("displayport") != std::string::npos) {
        return "DisplayPort";
    } else if (port_lower.find("vga") != std::string::npos) {
        return "VGA";
    } else if (port_lower.find("dvi") != std::string::npos) {
        return "DVI";
    } else if (port_lower.find("usb") != std::string::npos) {
        return "USB-C";
    } else if (port_lower.find("embedded") != std::string::npos) {
        return "Embedded (Laptop)";
    }
    
    return "Unknown";
}

// ==================== Проверка здоровья монитора ====================
MonitorAnalyzer::MonitorHealth MonitorAnalyzer::check_monitor_health(const MonitorInfo& monitor) {
    MonitorHealth health;
    health.is_healthy = true;
    health.health_score = 100;
    
    // Обнаруживаем проблемы
    health.issues = detect_monitor_issues(monitor);
    
    // Вычисляем общий статус
    if (health.issues.empty()) {
        health.overall_status = "Healthy";
        health.is_healthy = true;
        health.health_score = 100;
    } else if (health.issues.size() <= 2) {
        health.overall_status = "Minor Issues";
        health.is_healthy = true;
        health.health_score = 80;
    } else if (health.issues.size() <= 4) {
        health.overall_status = "Some Issues";
        health.is_healthy = false;
        health.health_score = 60;
    } else {
        health.overall_status = "Major Issues";
        health.is_healthy = false;
        health.health_score = 40;
    }
    
    return health;
}

// ==================== Проверка подключения монитора ====================
bool MonitorAnalyzer::is_monitor_connected(const std::string& port) {
    try {
        std::string drm_path = "/sys/class/drm/" + port;
        return fs::exists(drm_path + "/status");
    } catch (const std::exception& e) {
        std::cerr << "Error checking monitor connection: " << e.what() << std::endl;
    }
    return false;
}

// ==================== Получение EDID информации ====================
std::string MonitorAnalyzer::get_edid_info(const std::string& port) {
    std::string edid;
    
    try {
        // Пытаемся прочитать EDID из /sys/class/drm
        std::string drm_path = "/sys/class/drm/" + port;
        std::string edid_file = drm_path + "/edid";
        
        if (fs::exists(edid_file)) {
            std::ifstream file(edid_file, std::ios::binary);
            if (file.is_open()) {
                std::stringstream buffer;
                buffer << file.rdbuf();
                edid = buffer.str();
                file.close();
            }
        }
    } catch (const std::exception& e) {
        std::cerr << "Error reading EDID: " << e.what() << std::endl;
    }
    
    return edid;
}

// ==================== Обнаружение проблем с монитором ====================
std::vector<std::string> MonitorAnalyzer::detect_monitor_issues(const MonitorInfo& monitor) {
    std::vector<std::string> issues;
    
    // Проверка подключения
    if (!monitor.is_connected) {
        issues.push_back("Monitor not connected");
    }
    
    // Проверка включения
    if (monitor.is_connected && !monitor.is_enabled) {
        issues.push_back("Monitor connected but disabled");
    }
    
    // Проверка разрешения
    if (monitor.width == 0 || monitor.height == 0) {
        issues.push_back("No resolution detected");
    } else if (monitor.width < 1024 || monitor.height < 768) {
        issues.push_back("Low resolution detected");
    }
    
    // Проверка частоты обновления
    if (monitor.refresh_rate == 0) {
        issues.push_back("No refresh rate detected");
    } else if (monitor.refresh_rate < 60) {
        issues.push_back("Low refresh rate (< 60 Hz)");
    }
    
    // Проверка EDID
    if (monitor.edid.empty()) {
        issues.push_back("No EDID information available");
    }
    
    // Проверка производителя
    if (monitor.manufacturer.empty() || monitor.manufacturer == "Unknown") {
        issues.push_back("Manufacturer information not available");
    }
    
    // Проверка модели
    if (monitor.model.empty()) {
        issues.push_back("Model information not available");
    }
    
    // Проверка типа подключения
    if (monitor.connection == "Unknown") {
        issues.push_back("Connection type not detected");
    }
    
    // Если это встроенный монитор ноутбука, проверяем другие условия
    if (monitor.connection == "Embedded (Laptop)") {
        if (!monitor.is_primary) {
            issues.push_back("Laptop monitor is not primary");
        }
    }
    
    return issues;
}

// ==================== Вычисление оценки здоровья ====================
int MonitorAnalyzer::calculate_health_score(const MonitorInfo& monitor, const std::vector<std::string>& issues) {
    int score = 100;
    
    // Вычитаем баллы за каждую проблему
    for (const auto& issue : issues) {
        if (issue.find("not connected") != std::string::npos) {
            score -= 50;
        } else if (issue.find("disabled") != std::string::npos) {
            score -= 30;
        } else if (issue.find("No resolution") != std::string::npos) {
            score -= 40;
        } else if (issue.find("Low resolution") != std::string::npos) {
            score -= 20;
        } else if (issue.find("No refresh rate") != std::string::npos) {
            score -= 30;
        } else if (issue.find("Low refresh rate") != std::string::npos) {
            score -= 15;
        } else if (issue.find("No EDID") != std::string::npos) {
            score -= 20;
        } else if (issue.find("Manufacturer") != std::string::npos) {
            score -= 10;
        } else if (issue.find("Model") != std::string::npos) {
            score -= 10;
        } else if (issue.find("Connection type") != std::string::npos) {
            score -= 15;
        } else {
            score -= 10;
        }
    }
    
    // Убеждаемся, что оценка не отрицательная
    return std::max(0, score);
}
