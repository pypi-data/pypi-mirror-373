#pragma once

#include <memory>

namespace Amulet {

template <typename T>
struct is_unique_ptr : std::false_type { };

template <typename T>
struct is_unique_ptr<std::unique_ptr<T>> : std::true_type { };

template <typename T>
constexpr bool is_unique_ptr_v = is_unique_ptr<T>::value;

template <typename T>
struct is_shared_ptr : std::false_type { };

template <typename T>
struct is_shared_ptr<std::shared_ptr<T>> : std::true_type { };

template <typename T>
constexpr bool is_shared_ptr_v = is_shared_ptr<T>::value;

template <typename T>
struct is_weak_ptr : std::false_type { };

template <typename T>
struct is_weak_ptr<std::weak_ptr<T>> : std::true_type { };

template <typename T>
constexpr bool is_weak_ptr_v = is_weak_ptr<T>::value;

template <typename T>
void del(T*& ptr)
{
    if (ptr) {
        delete ptr;
        ptr = nullptr;
    }
}

template <typename T>
void move(T*& src, T*& dst)
{
    // Delete the original value
    del(dst);
    // Copy
    dst = src;
    // erase old ptr
    src = nullptr;
}

} // namespace Amulet
