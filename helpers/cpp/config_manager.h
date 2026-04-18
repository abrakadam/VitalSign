#ifndef CONFIG_MANAGER_H
#define CONFIG_MANAGER_H

#include <string>
#include <vector>
#include <map>
#include <fstream>
#include <sstream>

class ConfigManager {
public:
    static std::string get_config_dir();
    static bool create_config_dir();
    static bool save_config(const std::string& key, const std::string& value);
    static std::string load_config(const std::string& key);
    static bool delete_config(const std::string& key);
    static std::map<std::string, std::string> load_all_configs();
    static bool save_all_configs(const std::map<std::string, std::string>& configs);
    static bool clear_config();
    static std::string get_locale_path();
    static bool save_locale_data(const std::string& language, const std::string& data);
    static std::string load_locale_data(const std::string& language);
    static std::vector<std::string> get_available_locales();
    
private:
    static std::string config_dir;
    static std::string config_file;
};

#endif
