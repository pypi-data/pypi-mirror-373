// MIT Licence
// Based on https://github.com/KaganCanSit/Cross-Compatible-FileLock-Windows-and-Linux

#include <concepts>
#include <filesystem>
#include <stdexcept>
#include <string>
#include <type_traits>

#include "lock_file.hpp"
#include "memory.hpp"

#if defined(_WIN32) || defined(_WIN64)
#define NOMINMAX
#include <windows.h>

// Returns the last Win32 error, in string format. Returns an empty string if there is no error.
// https://stackoverflow.com/questions/1387064/how-to-get-the-error-message-from-the-error-code-returned-by-getlasterror
static std::string GetLastErrorAsString()
{
    // Get the error message ID, if any.
    DWORD errorMessageID = ::GetLastError();
    if (errorMessageID == 0) {
        return std::string(); // No error message has been recorded
    }

    LPSTR messageBuffer = nullptr;

    // Ask Win32 to give us the string version of that message ID.
    // The parameters we pass in, tell Win32 to create the buffer that holds the message for us (because we don't yet know how long the message string will be).
    size_t size = FormatMessageA(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
        NULL, errorMessageID, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), (LPSTR)&messageBuffer, 0, NULL);

    // Copy the error message into a std::string.
    std::string message(messageBuffer, size);

    // Free the Win32's string's buffer.
    LocalFree(messageBuffer);

    return message;
}

namespace Amulet {

class LockFilePrivate final {
public:
    LockFilePrivate(const std::filesystem::path& path, bool automatically_lock = true)
        : path(path)
        , file_handle(INVALID_HANDLE_VALUE)
    {
        if (automatically_lock) {
            lock_file();
        }
    }

    LockFilePrivate(const LockFilePrivate&) = delete;
    LockFilePrivate(LockFilePrivate&& other)
    {
        path = std::move(other.path);
        file_handle = other.file_handle;
        other.file_handle = INVALID_HANDLE_VALUE;
    };
    LockFilePrivate& operator=(const LockFilePrivate&) = delete;
    LockFilePrivate& operator=(LockFilePrivate&&) = default;

    ~LockFilePrivate() noexcept
    {
        unlock_file();
    };

    void lock_file()
    {
        if (file_handle != INVALID_HANDLE_VALUE) {
            throw std::runtime_error("File is already open.");
        }
        file_handle = CreateFileW(path.wstring().c_str(), GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        if (file_handle == INVALID_HANDLE_VALUE) {
            throw std::runtime_error("Could not open and lock file. Error: " + GetLastErrorAsString() + ", Path: " + path.string());
        }
    };

    void write_to_file(std::string_view value)
    {
        if (file_handle == INVALID_HANDLE_VALUE) {
            throw std::runtime_error("File is not open.");
        }
        DWORD written_size = 0;
        auto success = WriteFile(file_handle, value.data(), static_cast<DWORD>(value.size()), &written_size, NULL);
        if (success == FALSE || value.size() != written_size) {
            throw std::runtime_error("Error writing value.");
        }
    }

    void unlock_file() noexcept
    {
        if (file_handle != INVALID_HANDLE_VALUE) {
            CloseHandle(file_handle);
            file_handle = INVALID_HANDLE_VALUE;
        }
    };

private:
    std::filesystem::path path;
    HANDLE file_handle;
};

} // namespace Amulet

#elif defined(__unix__) || defined(__linux__) || defined(__APPLE__)

#include <errno.h>
#include <fcntl.h>
#include <sys/file.h>
#include <unistd.h>

namespace Amulet {

class LockFilePrivate final {
public:
    LockFilePrivate(const std::filesystem::path& path, bool automatically_lock = true)
        : path(path)
        , file_descriptor(-1)
    {
        if (automatically_lock) {
            lock_file();
        }
    };

    LockFilePrivate(const LockFilePrivate&) = delete;
    LockFilePrivate(LockFilePrivate&& other)
    {
        path = std::move(other.path);
        file_descriptor = other.file_descriptor;
        other.file_descriptor = -1;
    }
    LockFilePrivate& operator=(LockFilePrivate&&) = default;

    ~LockFilePrivate() noexcept
    {
        unlock_file();
    };

    void lock_file()
    {
        if (file_descriptor != -1) {
            throw std::runtime_error("File is already open.");
        }
        file_descriptor = open(path.c_str(), O_RDWR | O_CREAT | O_TRUNC, 0666);
        if (file_descriptor == -1) {
            throw std::runtime_error("Could not open file. Code: " + std::to_string(errno) + ", Path: " + path.string());
        }
        if (flock(file_descriptor, LOCK_EX | LOCK_NB) == -1) {
            int error_code = errno;
            close(file_descriptor);
            file_descriptor = -1;
            throw std::runtime_error("Could not lock file. Code: " + std::to_string(errno) + ", Path: " + path.string());
        }
    };

    void write_to_file(std::string_view value)
    {
        if (file_descriptor == -1) {
            throw std::runtime_error("File is not open.");
        }
        if (value.size() != write(file_descriptor, value.data(), value.size())) {
            throw std::runtime_error("Error writing value. Code: " + std::to_string(errno));
        }
    }

    void unlock_file() noexcept
    {
        if (file_descriptor != -1) {
            flock(file_descriptor, LOCK_UN);
            close(file_descriptor);
            file_descriptor = -1;
        }
    };

private:
    std::filesystem::path path;
    int file_descriptor;
};

} // namespace Amulet

#else

static_assert(false, "Unsupported platform.");

#endif

namespace {

template <typename T>
concept FileLockConcept = requires(T l, const std::string& value) {
    { l.~T() } noexcept;
    { l.lock_file() } -> std::same_as<void>;
    { l.write_to_file(value) } -> std::same_as<void>;
    { l.unlock_file() } noexcept -> std::same_as<void>;
};

static_assert(!std::is_copy_constructible_v<Amulet::LockFilePrivate>);
static_assert(std::is_move_constructible_v<Amulet::LockFilePrivate>);
static_assert(std::constructible_from<Amulet::LockFilePrivate, std::filesystem::path, bool>);
static_assert(FileLockConcept<Amulet::LockFilePrivate>);

} // namespace

namespace Amulet {

LockFile::LockFile(const std::filesystem::path& path, bool automatically_lock)
    : ptr(new LockFilePrivate(path, automatically_lock))
{
}

LockFile::LockFile(LockFile&& other)
{
    move(other.ptr, ptr);
}

LockFile& LockFile::operator=(LockFile&& other)
{
    move(other.ptr, ptr);
    return *this;
}

LockFile::~LockFile()
{
    del(ptr);
}

void LockFile::lock_file()
{
    ptr->lock_file();
}

void LockFile::write_to_file(std::string_view value)
{
    ptr->write_to_file(value);
}

void LockFile::unlock_file()
{
    ptr->unlock_file();
}

} // namespace Amulet
