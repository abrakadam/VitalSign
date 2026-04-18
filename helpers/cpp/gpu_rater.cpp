/**
 * C++ Helper для оценки видеокарты
 * 
 * Этот модуль предоставляет функции для оценки производительности видеокарты
 * на основе её характеристик.
 */

#include <string>
#include <map>
#include <algorithm>
#include <sstream>
#include <fstream>
#include <vector>

class GPURater {
public:
    struct GPUInfo {
        std::string name;
        int vram;
        bool is_integrated;
        int score;
        std::string rating;
        std::string category;
        bool estimated;
    };

    // База данных видеокарт с оценками
    static std::map<std::string, int> get_gpu_database() {
        static std::map<std::string, int> database = {
            // NVIDIA RTX 40 series
            {"rtx 4090", 100},
            {"rtx 4080", 95},
            {"rtx 4070 ti", 90},
            {"rtx 4070", 85},
            {"rtx 4060 ti", 78},
            {"rtx 4060", 72},
            // NVIDIA RTX 30 series
            {"rtx 3090 ti", 95},
            {"rtx 3090", 92},
            {"rtx 3080 ti", 90},
            {"rtx 3080", 88},
            {"rtx 3070 ti", 85},
            {"rtx 3070", 82},
            {"rtx 3060 ti", 78},
            {"rtx 3060", 72},
            {"rtx 3050", 60},
            // NVIDIA RTX 20 series
            {"rtx 2080 ti", 75},
            {"rtx 2080", 72},
            {"rtx 2070", 68},
            {"rtx 2060", 65},
            // NVIDIA GTX 16 series
            {"gtx 1660 ti", 58},
            {"gtx 1660", 55},
            {"gtx 1650", 45},
            // NVIDIA GTX 10 series
            {"gtx 1080 ti", 62},
            {"gtx 1080", 58},
            {"gtx 1070", 55},
            {"gtx 1060", 48},
            {"gtx 1050 ti", 40},
            {"gtx 1050", 35},
            // AMD RX 7000 series
            {"rx 7900 xtx", 98},
            {"rx 7900 xt", 95},
            {"rx 7800 xt", 88},
            {"rx 7700 xt", 82},
            {"rx 7600", 72},
            // AMD RX 6000 series
            {"rx 6950 xt", 88},
            {"rx 6900 xt", 85},
            {"rx 6800 xt", 82},
            {"rx 6800", 78},
            {"rx 6750 xt", 72},
            {"rx 6700 xt", 70},
            {"rx 6600 xt", 65},
            {"rx 6600", 60},
            {"rx 6500 xt", 45},
            // AMD RX 5000 series
            {"rx 5700 xt", 68},
            {"rx 5700", 65},
            {"rx 5600 xt", 58},
            {"rx 5500 xt", 48},
            // AMD RX Vega
            {"rx vega 64", 52},
            {"rx vega 56", 50},
            // AMD RX 500 series
            {"rx 580", 42},
            {"rx 570", 38},
            {"rx 560", 32},
            // AMD RX 400 series
            {"rx 480", 40},
            {"rx 470", 38},
            // NVIDIA старые
            {"gtx 980 ti", 45},
            {"gtx 980", 42},
            {"gtx 970", 40},
            {"gtx 960", 35},
            {"gtx 780", 28},
            // Интегрированная графика
            {"intel iris", 15},
            {"intel uhd", 10},
            {"intel hd", 8},
            {"amd radeon vega", 12},
            {"amd radeon graphics", 15},
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

    static int estimate_gpu_score(int vram) {
        if (vram >= 24 * 1024) return 90;  // 24GB+
        if (vram >= 16 * 1024) return 80;  // 16GB
        if (vram >= 12 * 1024) return 70;  // 12GB
        if (vram >= 8 * 1024) return 60;   // 8GB
        if (vram >= 6 * 1024) return 50;   // 6GB
        if (vram >= 4 * 1024) return 40;   // 4GB
        if (vram >= 2 * 1024) return 25;   // 2GB
        return 15;
    }

    static bool is_integrated_gpu(std::string gpu_name) {
        std::string gpu_name_lower = to_lower(gpu_name);
        
        // Intel встроенная графика
        if (gpu_name_lower.find("intel iris") != std::string::npos ||
            gpu_name_lower.find("intel uhd") != std::string::npos ||
            gpu_name_lower.find("intel hd") != std::string::npos ||
            gpu_name_lower.find("intel graphics") != std::string::npos) {
            return true;
        }
        
        // AMD встроенная графика (APU)
        if (gpu_name_lower.find("amd radeon vega") != std::string::npos ||
            gpu_name_lower.find("amd radeon graphics") != std::string::npos ||
            gpu_name_lower.find("radeon vega") != std::string::npos) {
            return true;
        }
        
        // Другие встроенные
        if (gpu_name_lower.find("igpu") != std::string::npos ||
            gpu_name_lower.find("integrated") != std::string::npos ||
            gpu_name_lower.find("apu") != std::string::npos) {
            return true;
        }
        
        return false;
    }

    static GPUInfo rate_gpu(std::string gpu_name, int vram = 0, bool is_integrated = false) {
        GPUInfo info;
        info.name = gpu_name;
        info.vram = vram;
        info.is_integrated = is_integrated;
        info.estimated = false;
        
        std::string gpu_name_lower = to_lower(gpu_name);
        auto database = get_gpu_database();
        
        // Ищем в базе данных
        for (const auto& entry : database) {
            if (gpu_name_lower.find(entry.first) != std::string::npos) {
                info.score = entry.second;
                // Если это встроенная карта, снижаем оценку
                if (is_integrated) {
                    info.score = (int)(info.score * 0.6);
                }
                info.rating = get_rating_description(info.score);
                info.category = get_category(info.score);
                return info;
            }
        }
        
        // Если не найдено в базе, оцениваем по VRAM
        if (vram > 0) {
            info.score = estimate_gpu_score(vram);
            // Если это встроенная карта, снижаем оценку
            if (is_integrated) {
                info.score = (int)(info.score * 0.6);
            }
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

    // Чтение информации о GPU из lspci
    static std::vector<GPUInfo> get_gpu_info_from_system() {
        std::vector<GPUInfo> gpus;
        
        // Здесь можно добавить чтение из /proc/bus/pci/devices или вызов lspci
        // Для упрощения вернем пустой вектор
        return gpus;
    }
};
