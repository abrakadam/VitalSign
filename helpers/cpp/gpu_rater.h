/**
 * C++ Helper для оценки видеокарты - Заголовочный файл
 */

#ifndef GPU_RATER_H
#define GPU_RATER_H

#include <string>
#include <map>
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

    static std::map<std::string, int> get_gpu_database();
    static std::string to_lower(std::string str);
    static std::string get_rating_description(int score);
    static std::string get_category(int score);
    static int estimate_gpu_score(int vram);
    static bool is_integrated_gpu(std::string gpu_name);
    static GPUInfo rate_gpu(std::string gpu_name, int vram = 0, bool is_integrated = false);
    static std::vector<GPUInfo> get_gpu_info_from_system();
};

#endif // GPU_RATER_H
