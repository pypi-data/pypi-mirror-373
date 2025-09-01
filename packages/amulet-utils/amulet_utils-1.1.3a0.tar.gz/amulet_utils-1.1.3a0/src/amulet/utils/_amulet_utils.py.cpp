#include <pybind11/pybind11.h>

#include <amulet/pybind11_extensions/compatibility.hpp>
#include <amulet/utils/python.hpp>

namespace py = pybind11;
namespace pyext = Amulet::pybind11_extensions;

void init_numpy(py::module);
void init_event(py::module);
void init_task_manager(py::module);
void init_lock(py::module);
void init_logging(py::module);
void init_image(py::module);
void init_matrix(py::module);

void init_module(py::module m)
{
    pyext::init_compiler_config(m);

    auto py_valid = Amulet::get_py_valid();
    *py_valid = true;
    py::module::import("atexit").attr("register")(
        py::cpp_function([py_valid]() { *py_valid = false; }));

    // Submodules
    init_numpy(m);
    init_event(m);
    init_task_manager(m);
    init_lock(m);
    init_logging(m);
    init_image(m);
    init_matrix(m);
}

PYBIND11_MODULE(_amulet_utils, m)
{
    py::options options;
    options.disable_function_signatures();
    m.def("init", &init_module, py::doc("init(arg0: types.ModuleType) -> None"));
    options.enable_function_signatures();
}
