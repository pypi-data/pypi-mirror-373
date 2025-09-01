#pragma once

#include <filesystem>
#include <memory>
#include <string>

#include <amulet/utils/dll.hpp>

#include "lock_file.hpp"

namespace Amulet {

// Get the directory in which temporary directories will be created.
// This is configurable by setting the "CACHE_DIR" environment variable.
// Thread safe.
AMULET_UTILS_EXPORT std::filesystem::path get_temp_dir();

// A temporary directory to do with as you wish.
class TempDir {
private:
    std::filesystem::path _path;
    std::unique_ptr<Amulet::LockFile> _lock;

public:
    // Construct a new temporary directory.
    // Thread safe.
    AMULET_UTILS_EXPORT TempDir(const std::string& group);

    // Delete copy constructors
    TempDir(const TempDir&) = delete;
    TempDir& operator=(const TempDir&) = delete;

    // Move constructors
    AMULET_UTILS_EXPORT TempDir(TempDir&&);
    AMULET_UTILS_EXPORT TempDir& operator=(TempDir&&);

    // TempDir destructor.
    // This automatically deletes the temporary directory.
    AMULET_UTILS_EXPORT ~TempDir();

    // Get the path of the temporary directory.
    // Thread safe.
    AMULET_UTILS_EXPORT const std::filesystem::path& get_path() const;
};

} // namespace Amulet
