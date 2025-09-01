#include <pybind11/pybind11.h>

#include <filesystem>

#include <amulet/pybind11_extensions/py_module.hpp>

#include "image.hpp"

namespace py = pybind11;

void init_image(py::module m_parent)
{
    try {
        py::module::import("PIL.Image");
    } catch (py::error_already_set& e) {
        if (e.matches(PyExc_ImportError)) {
            return;
        } else {
            throw;
        }
    }

    auto m = Amulet::pybind11_extensions::def_subpackage(m_parent, "image");
    py::list __path__ = m.attr("__path__");
    std::filesystem::path path = __path__[0].cast<std::string>();

    m.def("get_missing_no_icon", &Amulet::get_missing_no_icon);

    m.attr("missing_no_icon_path") = py::cast((path / "missing_no.png").string());
}
