#include <pybind11/pybind11.h>

#include <string>

#include <amulet/pybind11_extensions/py_module.hpp>
#include <amulet/utils/logging/logging.hpp>
#include <amulet/utils/event/event.py.hpp>

namespace py = pybind11;
namespace pyext = Amulet::pybind11_extensions;

void init_logging(py::module m_parent)
{
    auto m = pyext::def_subpackage(m_parent, "logging");

    m.def(
        "register_default_log_handler",
        &Amulet::register_default_log_handler,
        py::doc("Register the default log handler.\n"
                "This is registered by default with a log level of 20.\n"
                "Thread safe."));
    m.def(
        "unregister_default_log_handler",
        &Amulet::unregister_default_log_handler,
        py::doc("Unregister the default log handler.\n"
                "Thread safe."));
    m.def(
        "get_min_log_level",
        &Amulet::get_min_log_level,
        py::doc("Get the maximum message level that will be logged.\n"
                "Registered handlers may be more strict.\n"
                "Thread safe."));
    m.def(
        "set_min_log_level",
        &Amulet::set_min_log_level,
        py::arg("level"),
        py::doc("Set the maximum message level that will be logged.\n"
                "Registered handlers may be more strict.\n"
                "Thread safe."));

    Amulet::create_event_binding<Amulet::Event<int, std::string>>();

    m.def(
        "get_logger",
        []() -> Amulet::PyEvent<int, std::string> { return py::cast(Amulet::get_logger(), py::return_value_policy::reference); },
        py::doc("Get the logger event.\n"
                "This is emitted with the message and its level every time a message is logged."));

    py::module::import("amulet.utils.logging._logging");
}
