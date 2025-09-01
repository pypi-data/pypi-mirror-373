#include <iostream>
#include <mutex>
#include <string>

#include "logging.hpp"

namespace Amulet {

int& get_min_log_level()
{
    static int min_log_level = 20;
    return min_log_level;
}

void set_min_log_level(int level)
{
    get_min_log_level() = level;
}

static std::mutex& get_default_log_mutex() {
    static std::mutex log_mutex;
    return log_mutex;
}

static Amulet::EventToken<int, std::string>& get_default_log_handler_token() {
    static Amulet::EventToken<int, std::string> default_log_handler_token;
    return default_log_handler_token;
}

static void default_log_handler(int level, const std::string& msg)
{
    std::unique_lock lock(get_default_log_mutex());
    std::cout << msg << std::endl;
}

Amulet::Event<int, std::string>& get_logger()
{
    // Initialise dependent global variables
    get_min_log_level();
    get_default_log_mutex();
    get_default_log_handler_token();
    static Amulet::Event<int, std::string> logger;
    // Setup the default log handler.
    static bool init_hanler = true;
    if (init_hanler) {
        get_default_log_handler_token() = logger.connect(default_log_handler);
        init_hanler = false;
    }
    return logger;
}

void log(int level, const std::string& msg)
{
    if (get_min_log_level() <= level) {
        get_logger().dispatch(level, msg);
    }
}

void debug(const std::string& msg)
{
    log(10, msg);
}

void info(const std::string& msg)
{
    log(20, msg);
}

void warning(const std::string& msg)
{
    log(30, msg);
}

void error(const std::string& msg)
{
    log(40, msg);
}

void critical(const std::string& msg)
{
    log(50, msg);
}

void register_default_log_handler()
{
    get_default_log_handler_token() = get_logger().connect(default_log_handler);
}

void unregister_default_log_handler()
{
    get_logger().disconnect(get_default_log_handler_token());
}

} // namespace Amulet
