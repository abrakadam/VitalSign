/**
 * C++ Helper для оценки процессора
 * 
 * Этот модуль предоставляет функции для оценки производительности процессора
 * на основе его характеристик.
 */

#include <string>
#include <map>
#include <algorithm>
#include <sstream>
#include <fstream>
#include <vector>

class CPURater {
public:
    struct CPUInfo {
        std::string name;
        int cores;
        double frequency;
        std::string architecture;
        int score;
        std::string rating;
        std::string category;
        bool estimated;
    };

    // База данных процессоров с оценками
    static std::map<std::string, int> get_cpu_database() {
        static std::map<std::string, int> database = {
            // AMD Ryzen 9
            {"ryzen 9 7950x", 100},
            {"ryzen 9 7900x", 95},
            {"ryzen 9 5950x", 98},
            {"ryzen 9 5900x", 92},
            {"ryzen 9 3950x", 85},
            {"ryzen 9 3900x", 82},
            // AMD Ryzen 7
            {"ryzen 7 7800x3d", 100},
            {"ryzen 7 7700x", 90},
            {"ryzen 7 5800x3d", 95},
            {"ryzen 7 5800x", 88},
            {"ryzen 7 5700x", 85},
            {"ryzen 7 3700x", 78},
            {"ryzen 7 3800x", 80},
            // AMD Ryzen 5
            {"ryzen 5 7600x", 85},
            {"ryzen 5 5600x", 82},
            {"ryzen 5 5500", 70},
            {"ryzen 5 3600", 75},
            {"ryzen 5 2600", 60},
            // Intel Core i9
            {"i9-14900k", 100},
            {"i9-13900k", 98},
            {"i9-12900k", 92},
            {"i9-10900k", 80},
            {"i9-9900k", 75},
            // Intel Core i7
            {"i7-14700k", 95},
            {"i7-13700k", 92},
            {"i7-12700k", 88},
            {"i7-12700", 85},
            {"i7-11700k", 82},
            {"i7-10700k", 78},
            {"i7-9700k", 72},
            // Intel Core i5
            {"i5-14600k", 88},
            {"i5-13600k", 85},
            {"i5-12600k", 82},
            {"i5-12400", 78},
            {"i5-11400", 72},
            {"i5-10400", 68},
            {"i5-9600k", 65},
            {"i5-9400f", 60},
            // Intel Core i3
            {"i3-13100", 60},
            {"i3-12100", 58},
            {"i3-10100", 50},
            // Intel старые
            {"i7-8700k", 68},
            {"i7-7700k", 62},
            {"i5-8400", 55},
            {"i5-7500", 50},
            // AMD старые
            {"ryzen 1700", 55},
            {"ryzen 1600", 52},
            // AMD FX
            {"fx-9590", 35},
            {"fx-8350", 32},
            // AMD APU
            {"athlon", 20},
            {"a10", 25},
            {"a8", 22},
        };
        return database;
    }

    static std::string to_lower(std::string str) {
        std::transform(str.begin(), str.end(), str.begin(), ::tolower);
        return str;
    }

    static std::string get_rating_description(int score) {
        if (score >= 90) return "Отлично";
        if (score >= 75) return "Очень хорошо";
        if (score >= 60) return "Хорошо";
        if (score >= 45) return "Средне";
        if (score >= 30) return "Ниже среднего";
        if (score > 0) return "Слабо";
        return "Неизвестно";
    }

    static std::string get_category(int score) {
        if (score >= 90) return "flagship";
        if (score >= 75) return "high_end";
        if (score >= 60) return "mid_range";
        if (score >= 45) return "entry_level";
        if (score > 0) return "budget";
        return "unknown";
    }

    static int estimate_cpu_score(int cores, double freq) {
        int base_score = cores * 5;
        int freq_bonus = (int)freq * 2;
        int multi_bonus = 0;
        
        if (cores >= 16) multi_bonus = 20;
        else if (cores >= 12) multi_bonus = 15;
        else if (cores >= 8) multi_bonus = 10;
        else if (cores >= 6) multi_bonus = 5;
        
        int total = base_score + freq_bonus + multi_bonus;
        return std::min(total, 85);
    }

    static CPUInfo rate_cpu(std::string cpu_name, int cores = 0, double freq = 0) {
        CPUInfo info;
        info.name = cpu_name;
        info.cores = cores;
        info.frequency = freq;
        info.architecture = "Unknown";
        info.estimated = false;
        
        std::string cpu_name_lower = to_lower(cpu_name);
        auto database = get_cpu_database();
        
        // Ищем в базе данных
        for (const auto& entry : database) {
            if (cpu_name_lower.find(entry.first) != std::string::npos) {
                info.score = entry.second;
                info.rating = get_rating_description(info.score);
                info.category = get_category(info.score);
                return info;
            }
        }
        
        // Если не найдено, оцениваем по характеристикам
        if (cores > 0 && freq > 0) {
            info.score = estimate_cpu_score(cores, freq);
            info.rating = get_rating_description(info.score);
            info.category = get_category(info.score);
            info.estimated = true;
            return info;
        }
        
        // Если нет данных
        info.score = 0;
        info.rating = "Неизвестно";
        info.category = "unknown";
        return info;
    }

    // Чтение информации о CPU из /proc/cpuinfo
    static CPUInfo get_cpu_info_from_system() {
        CPUInfo info;
        info.name = "Unknown CPU";
        info.cores = 0;
        info.frequency = 0.0;
        info.architecture = "Unknown";
        
        std::ifstream cpuinfo("/proc/cpuinfo");
        std::string line;
        
        while (std::getline(cpuinfo, line)) {
            if (line.find("model name") != std::string::npos) {
                size_t pos = line.find(':');
                if (pos != std::string::npos) {
                    info.name = line.substr(pos + 2);
                }
            } else if (line.find("cpu cores") != std::string::npos) {
                size_t pos = line.find(':');
                if (pos != std::string::npos) {
                    info.cores = std::stoi(line.substr(pos + 2));
                }
            } else if (line.find("cpu MHz") != std::string::npos) {
                size_t pos = line.find(':');
                if (pos != std::string::npos) {
                    info.frequency = std::stod(line.substr(pos + 2)) / 1000.0;
                }
            }
        }
        
        // Оцениваем CPU
        CPUInfo rated = rate_cpu(info.name, info.cores, info.frequency);
        info.score = rated.score;
        info.rating = rated.rating;
        info.category = rated.category;
        info.estimated = rated.estimated;
        
        return info;
    }
};
