/**
 * C++ Helper для оценки процессора - Заголовочный файл
 */

#ifndef CPU_RATER_H
#define CPU_RATER_H

#include <string>
#include <map>

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

    static std::map<std::string, int> get_cpu_database();
    static std::string to_lower(std::string str);
    static std::string get_rating_description(int score);
    static std::string get_category(int score);
    static int estimate_cpu_score(int cores, double freq);
    static CPUInfo rate_cpu(std::string cpu_name, int cores = 0, double freq = 0);
    static CPUInfo get_cpu_info_from_system();
};

#endif // CPU_RATER_H
