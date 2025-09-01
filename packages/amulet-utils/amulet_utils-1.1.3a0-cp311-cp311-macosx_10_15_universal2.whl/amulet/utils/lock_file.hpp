#pragma once

#include <filesystem>
#include <string_view>

#include <amulet/utils/dll.hpp>

namespace Amulet {

class LockFilePrivate;

class AMULET_UTILS_EXPORT LockFile final {
private:
    LockFilePrivate* ptr = nullptr;

public:
    LockFile(const std::filesystem::path& path, bool automatically_lock = true);
    LockFile(const LockFile&) = delete;
    LockFile(LockFile&&);
    LockFile& operator=(const LockFile&) = delete;
    LockFile& operator=(LockFile&&);

    ~LockFile();

    void lock_file();
    void write_to_file(std::string_view value);
    void unlock_file();
};

}
