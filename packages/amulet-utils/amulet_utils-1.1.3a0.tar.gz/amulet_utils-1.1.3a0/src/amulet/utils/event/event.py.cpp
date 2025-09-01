#include <pybind11/pybind11.h>

#include <amulet/utils/event/event.hpp>

namespace py = pybind11;

void init_event(py::module m_parent)
{
    // This is a bit janky
    // amulet.utils.event is a pure python package but we need
    // to define a module inside it without importing it.
    const char* m_parent_name = PyModule_GetName(m_parent.ptr());
    if (m_parent_name == nullptr) {
        throw py::error_already_set();
    }
    std::string full_name = std::string(m_parent_name) + ".event._connection_mode";
    py::handle submodule = PyImport_AddModule(full_name.c_str());
    if (!submodule) {
        throw py::error_already_set();
    }
    auto m = py::reinterpret_borrow<py::module_>(submodule);

    // Initialise amulet.utils.event._connection_mode
    std::string module_name = m.attr("__name__").cast<std::string>();

    py::enum_<Amulet::ConnectionMode> ConnectionMode(m, "ConnectionMode");
    ConnectionMode.value(
        "Direct",
        Amulet::ConnectionMode::Direct,
        "Directly called by the emitter.");
    ConnectionMode.value(
        "Async",
        Amulet::ConnectionMode::Async,
        "Called asynchronously.");
    ConnectionMode.attr("__repr__") = py::cpp_function(
        [module_name, ConnectionMode](const py::object& arg) -> py::str {
            return py::str("{}.{}").format(module_name, ConnectionMode.attr("__str__")(arg));
        },
        py::name("__repr__"),
        py::is_method(ConnectionMode));

    // Import it so that stubgen picks it up.
    py::module::import("amulet.utils.event");
}
