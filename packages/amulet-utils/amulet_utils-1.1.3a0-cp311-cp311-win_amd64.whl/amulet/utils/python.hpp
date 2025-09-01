#pragma once

#include <memory>

#include <amulet/utils/dll.hpp>

namespace Amulet {

// Is the python interpreter valid.
// This will be false before the interpreter starts and after it shuts down and true while it is running.
AMULET_UTILS_EXPORT std::shared_ptr<bool> get_py_valid();

} // namespace Amulet
