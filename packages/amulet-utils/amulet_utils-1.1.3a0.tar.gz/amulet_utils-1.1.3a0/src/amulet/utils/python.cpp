#include "python.hpp"

namespace Amulet {

std::shared_ptr<bool> get_py_valid()
{
    static std::shared_ptr<bool> _py_valid = std::make_shared<bool>(false);
    return _py_valid;
}

} // namespace Amulet
