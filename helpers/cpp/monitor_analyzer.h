#ifndef MONITOR_ANALYZER_H
#define MONITOR_ANALYZER_H

#include <string>
#include <vector>
#include <map>

class MonitorAnalyzer {
public:
    struct MonitorInfo {
        std::string name;
        std::string model;
        std::string manufacturer;
        std::string serial;
        std::string connection;  // HDMI, DisplayPort, VGA, etc.
        int width;
        int height;
        int refresh_rate;
        bool is_primary;
        bool is_enabled;
        bool is_connected;
        std::string status;
        std::string edid;
    };

    struct MonitorHealth {
        bool is_healthy;
        std::vector<std::string> issues;
        std::string overall_status;
        int health_score;  // 0-100
    };

    static std::vector<MonitorInfo> get_monitors();
    static std::string get_connection_type(const std::string& port);
    static MonitorHealth check_monitor_health(const MonitorInfo& monitor);
    static bool is_monitor_connected(const std::string& port);
    static std::string get_edid_info(const std::string& port);
    static std::vector<std::string> detect_monitor_issues(const MonitorInfo& monitor);
    static int calculate_health_score(const MonitorInfo& monitor, const std::vector<std::string>& issues);
};

#endif
