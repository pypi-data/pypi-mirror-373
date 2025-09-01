#pragma once

#include <iostream>
#include <string>

#include <amulet/utils/dll.hpp>

namespace Amulet {

// Forward declare Event
template <typename... Args>
class Event;

// Register the default log handler.
// This is registered by default with a log level of 20.
// Thread safe.
AMULET_UTILS_EXPORT void register_default_log_handler();

// Unregister the default log handler.
// Thread safe.
AMULET_UTILS_EXPORT void unregister_default_log_handler();

// Get the maximum message level that will be logged.
// Registered handlers may be more strict.
// Thread safe.
AMULET_UTILS_EXPORT int& get_min_log_level();

// Set the maximum message level that will be logged.
// Registered handlers may be more strict.
// Thread safe.
AMULET_UTILS_EXPORT void set_min_log_level(int);

// Get the logger event.
// This is emitted with the message and its level every time a message is logged.
AMULET_UTILS_EXPORT Event<int, std::string>& get_logger();

// Log a message with a custom level.
// If the level is less than the configured log level this will do nothing.
// Thread safe.
AMULET_UTILS_EXPORT void log(int level, const std::string& msg);

// Log a message with debug level (10).
// Thread safe.
AMULET_UTILS_EXPORT void debug(const std::string& msg);

// Log a message with info level (20).
// Thread safe.
AMULET_UTILS_EXPORT void info(const std::string& msg);

// Log a message with warning level (30).
// Thread safe.
AMULET_UTILS_EXPORT void warning(const std::string& msg);

// Log a message with error level (40).
// Thread safe.
AMULET_UTILS_EXPORT void error(const std::string& msg);

// Log a message with info level (50).
// Thread safe.
AMULET_UTILS_EXPORT void critical(const std::string& msg);

}

// Some places can't use the normal logging system.
// This macro can be used to log directly.
#define AmuletLog(level, msg)                     \
    {                                       \
        if (get_min_log_level() <= level) { \
            std::cout << msg << std::endl;  \
        }                                   \
    }

#include <amulet/utils/event/event.hpp>
