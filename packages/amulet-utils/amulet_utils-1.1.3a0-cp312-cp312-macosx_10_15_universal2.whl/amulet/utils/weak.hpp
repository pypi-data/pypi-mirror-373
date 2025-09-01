#pragma once

#include <functional>
#include <list>
#include <memory>
#include <ranges>
#include <set>

#include <amulet/utils/memory.hpp>

namespace Amulet {

template <typename T>
using WeakList = std::list<std::weak_ptr<T>>;

template <typename T>
using WeakSet = std::set<std::weak_ptr<T>, std::owner_less<std::weak_ptr<T>>>;

template <typename WeakT>
    requires std::ranges::input_range<WeakT> && is_weak_ptr_v<std::ranges::range_value_t<WeakT>>
void for_each(WeakT& sequence, std::function<void(typename std::ranges::range_value_t<WeakT>::element_type&)> callback)
{
    auto it = sequence.begin();
    while (it != sequence.end()) {
        auto ptr = it->lock();
        if (ptr) {
            callback(*ptr);
            it++;
        } else {
            it = sequence.erase(it);
        }
    }
}

} // namespace Amulet
