#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <cstdint>

#include <amulet/pybind11_extensions/builtins.hpp>
#include <amulet/pybind11_extensions/numpy.hpp>

#include <amulet/utils/matrix.hpp>

namespace py = pybind11;
namespace pyext = Amulet::pybind11_extensions;

static py::object get_class(std::string lib_name, std::string cls_name)
{
    try {
        return py::module::import(lib_name.c_str()).attr(cls_name.c_str());
    } catch (py::error_already_set& e) {
        if (e.matches(PyExc_ImportError)) {
            // Return an empty py::object
            return {};
        } else {
            throw;
        }
    }
}

template <typename T>
Amulet::Matrix4x4 convert_buffer(py::buffer_info& info)
{
    auto i_step = info.strides[0] / sizeof(T);
    auto j_step = info.strides[1] / sizeof(T);
    const T* arr = static_cast<const T*>(info.ptr);
    Amulet::Matrix4x4 m;
    for (auto i = 0; i < 4; i++) {
        for (auto j = 0; j < 4; j++) {
            m.data[i][j] = static_cast<double>(*(arr + i_step * i + j_step * j));
        }
    }
    return m;
}

void init_matrix(py::module m_parent)
{
    auto m = m_parent.def_submodule("matrix");
    std::string m_name = m.attr("__name__").cast<std::string>();

    py::classh<Amulet::Matrix4x4> Matrix4x4(m, "Matrix4x4", py::buffer_protocol(),
        "A 4x4 transformation matrix.");

    Matrix4x4.def(
        py::init<>(),
        py::doc("Construct with uninitialised memory."));

    Matrix4x4.def(
        py::init(
            [](
                py::typing::Tuple<
                    py::typing::Tuple<double, double, double, double>,
                    py::typing::Tuple<double, double, double, double>,
                    py::typing::Tuple<double, double, double, double>,
                    py::typing::Tuple<double, double, double, double>>
                    array) {
                if (array.size() != 4) {
                    throw py::type_error("Tuple shape is incorrect");
                }
                auto get_line = [&array](std::uint8_t i) {
                    auto line = array[i].cast<py::tuple>();
                    if (line.size() != 4) {
                        throw py::type_error("Tuple shape is incorrect");
                    }
                    return line;
                };
                auto line_1 = get_line(0);
                auto line_2 = get_line(1);
                auto line_3 = get_line(2);
                auto line_4 = get_line(3);
                return Amulet::Matrix4x4 {
                    {
                        { line_1[0].cast<double>(), line_1[1].cast<double>(), line_1[2].cast<double>(), line_1[3].cast<double>() },
                        { line_2[0].cast<double>(), line_2[1].cast<double>(), line_2[2].cast<double>(), line_2[3].cast<double>() },
                        { line_3[0].cast<double>(), line_3[1].cast<double>(), line_3[2].cast<double>(), line_3[3].cast<double>() },
                        { line_4[0].cast<double>(), line_4[1].cast<double>(), line_4[2].cast<double>(), line_4[3].cast<double>() },
                    }
                };
            }),
        py::doc("Construct from tuples."));

    Matrix4x4.def(
        py::init<const Amulet::Matrix4x4&>(),
        py::arg("other"),
        py::doc("Copy from another matrix."));

    Matrix4x4.def(
        py::init([](py::buffer b) {
            py::buffer_info info = b.request();

            if (info.ndim != 2) {
                throw py::type_error("Expected a 2D buffer.");
            }
            if (info.shape[0] != 4 || info.shape[1] != 4) {
                throw py::type_error("Expected a 4x4 buffer.");
            }

            if (info.item_type_is_equivalent_to<double>()) {
                return convert_buffer<double>(info);
            } else if (info.item_type_is_equivalent_to<float>()) {
                return convert_buffer<float>(info);
            } else if (info.item_type_is_equivalent_to<std::int8_t>()) {
                return convert_buffer<std::int8_t>(info);
            } else if (info.item_type_is_equivalent_to<std::uint8_t>()) {
                return convert_buffer<std::uint8_t>(info);
            } else if (info.item_type_is_equivalent_to<std::int16_t>()) {
                return convert_buffer<std::int16_t>(info);
            } else if (info.item_type_is_equivalent_to<std::uint16_t>()) {
                return convert_buffer<std::uint16_t>(info);
            } else if (info.item_type_is_equivalent_to<std::int32_t>()) {
                return convert_buffer<std::int32_t>(info);
            } else if (info.item_type_is_equivalent_to<std::uint32_t>()) {
                return convert_buffer<std::uint32_t>(info);
            } else if (info.item_type_is_equivalent_to<std::int64_t>()) {
                return convert_buffer<std::int64_t>(info);
            } else if (info.item_type_is_equivalent_to<std::uint64_t>()) {
                return convert_buffer<std::uint64_t>(info);
            } else {
                throw py::type_error("Unknown buffer type " + info.format);
            }
        }));

    Matrix4x4.def(
        "__repr__",
        [m_name](const Amulet::Matrix4x4& self) {
            return m_name + ".Matrix4x4((("
                + std::to_string(self.data[0][0]) + ", "
                + std::to_string(self.data[0][1]) + ", "
                + std::to_string(self.data[0][2]) + ", "
                + std::to_string(self.data[0][3])
                + "), ("
                + std::to_string(self.data[1][0]) + ", "
                + std::to_string(self.data[1][1]) + ", "
                + std::to_string(self.data[1][2]) + ", "
                + std::to_string(self.data[1][3])
                + "), ("
                + std::to_string(self.data[2][0]) + ", "
                + std::to_string(self.data[2][1]) + ", "
                + std::to_string(self.data[2][2]) + ", "
                + std::to_string(self.data[2][3])
                + "), ("
                + std::to_string(self.data[3][0]) + ", "
                + std::to_string(self.data[3][1]) + ", "
                + std::to_string(self.data[3][2]) + ", "
                + std::to_string(self.data[3][3])
                + ")))";
        });

    Matrix4x4.def_buffer([](Amulet::Matrix4x4& self) {
        return py::buffer_info(
            self.data,
            sizeof(double),
            py::format_descriptor<double>::format(),
            2,
            { 4, 4 },
            { sizeof(double) * 4, sizeof(double) });
    });

    Matrix4x4.def_static(
        "identity_matrix",
        &Amulet::Matrix4x4::identity_matrix,
        py::doc("Construct a new identity matrix."));

    Matrix4x4.def_static(
        "scale_matrix",
        &Amulet::Matrix4x4::scale_matrix,
        py::arg("sx"),
        py::arg("sy"),
        py::arg("sz"),
        py::doc("Construct a new scale matrix."));

    Matrix4x4.def_static(
        "translation_matrix",
        &Amulet::Matrix4x4::translation_matrix,
        py::arg("dx"),
        py::arg("dy"),
        py::arg("dz"),
        py::doc("Construct a new translation matrix."));

    Matrix4x4.def_static(
        "rotation_x_matrix",
        &Amulet::Matrix4x4::rotation_x_matrix,
        py::arg("rx"),
        py::doc("Construct a new rotation matrix in the x axis."));

    Matrix4x4.def_static(
        "rotation_y_matrix",
        &Amulet::Matrix4x4::rotation_y_matrix,
        py::arg("ry"),
        py::doc("Construct a new rotation matrix in the y axis."));

    Matrix4x4.def_static(
        "rotation_z_matrix",
        &Amulet::Matrix4x4::rotation_z_matrix,
        py::arg("rz"),
        py::doc("Construct a new rotation matrix in the z axis."));

    Matrix4x4.def_static(
        "transformation_matrix",
        &Amulet::Matrix4x4::transformation_matrix,
        py::arg("sx"),
        py::arg("sy"),
        py::arg("sz"),
        py::arg("rx"),
        py::arg("ry"),
        py::arg("rz"),
        py::arg("dx"),
        py::arg("dy"),
        py::arg("dz"),
        py::doc("Construct a new transformation matrix made from scale, rotation and translation."));

    Matrix4x4.def(
        "get_element",
        &Amulet::Matrix4x4::get_element,
        py::arg("i"),
        py::arg("j"),
        py::doc("Get an element in the matrix."));

    Matrix4x4.def(
        "set_element",
        &Amulet::Matrix4x4::set_element,
        py::arg("i"),
        py::arg("j"),
        py::arg("value"),
        py::doc("Set an element in the matrix."));

    Matrix4x4.def(
        "__mul__",
        [](const Amulet::Matrix4x4& self, const Amulet::Matrix4x4& other) {
            return self * other;
        },
        py::arg("other"),
        py::doc("Multiply this matrix with another matrix."));

    Matrix4x4.def(
        "__mul__",
        [](
            const Amulet::Matrix4x4& self,
            py::typing::List<py::typing::Tuple<double, double, double>> py_other)
            -> py::typing::List<py::typing::Tuple<double, double, double>> {
            auto other_size = py_other.size();
            std::vector<std::array<double, 3>> other(other_size);
            for (auto v = 0; v < other_size; v++) {
                auto t = py_other[v].cast<py::tuple>();
                other[v][0] = t[0].cast<double>();
                other[v][1] = t[1].cast<double>();
                other[v][2] = t[2].cast<double>();
            }
            auto transformed = self * other;
            py::list py_transformed;
            for (const auto& vec : transformed) {
                py_transformed.append(py::make_tuple(vec[0], vec[1], vec[2]));
            }
            return py_transformed;
        },
        py::arg("other"),
        py::doc("Multiply this matrix with a sequence of vectors."));

    Matrix4x4.def(
        "translate",
        &Amulet::Matrix4x4::translate,
        py::arg("dx"),
        py::arg("dy"),
        py::arg("dz"),
        py::doc("Translate this matrix by the specified amount."));

    Matrix4x4.def(
        "scale",
        &Amulet::Matrix4x4::scale,
        py::arg("sx"),
        py::arg("sy"),
        py::arg("sz"),
        py::doc("Scale this matrix by the specified amount."));

    Matrix4x4.def(
        "rotate_x",
        &Amulet::Matrix4x4::rotate_x,
        py::arg("rx"),
        py::doc("Rotate this matrix by the specified amount in the x axis."));

    Matrix4x4.def(
        "rotate_y",
        &Amulet::Matrix4x4::rotate_y,
        py::arg("ry"),
        py::doc("Rotate this matrix by the specified amount in the y axis."));

    Matrix4x4.def(
        "rotate_z",
        &Amulet::Matrix4x4::rotate_z,
        py::arg("rz"),
        py::doc("Rotate this matrix by the specified amount in the z axis."));

    Matrix4x4.def(
        "decompose",
        &Amulet::Matrix4x4::decompose,
        py::doc("Decompose the matrix into scale, rotation and displacement tuples.\n"
                "Note that these values may be incorrect if the matrix is more complex\n"
                "Recompose the matrix and compare with the original to check"));

    Matrix4x4.def(
        "inverse",
        &Amulet::Matrix4x4::inverse,
        py::doc(
            "Compute the inverse of this matrix.\n"
            "Raises RuntimeError if the matrix cannot be inverted."));

    Matrix4x4.def(
        "almost_equal",
        &Amulet::Matrix4x4::almost_equal,
        py::arg("other"),
        py::arg("err") = 0.000001,
        py::doc("Check if this matrix is almost equal to another matrix."));

    if (auto QMatrix4x4 = get_class("PySide6.QtGui", "QMatrix4x4")) {
        Matrix4x4.def(
            py::init([](pyext::PyObjectStr<"PySide6.QtGui.QMatrix4x4"> other) {
                auto getitem = other.attr("__getitem__");
                auto m = [&getitem](std::uint8_t i, std::uint8_t j) {
                    return getitem(py::make_tuple(i, j)).cast<double>();
                };

                return Amulet::Matrix4x4 { {
                    { m(0, 0), m(0, 1), m(0, 2), m(0, 3) },
                    { m(1, 0), m(1, 1), m(1, 2), m(1, 3) },
                    { m(2, 0), m(2, 1), m(2, 2), m(2, 3) },
                    { m(3, 0), m(3, 1), m(3, 2), m(3, 3) },
                } };
            }));

        Matrix4x4.def(
            "to_qt",
            [QMatrix4x4](const Amulet::Matrix4x4& self) -> pyext::PyObjectStr<"PySide6.QtGui.QMatrix4x4"> {
                return QMatrix4x4(
                    self.data[0][0],
                    self.data[0][1],
                    self.data[0][2],
                    self.data[0][3],
                    self.data[1][0],
                    self.data[1][1],
                    self.data[1][2],
                    self.data[1][3],
                    self.data[2][0],
                    self.data[2][1],
                    self.data[2][2],
                    self.data[2][3],
                    self.data[3][0],
                    self.data[3][1],
                    self.data[3][2],
                    self.data[3][3]);
            });
    }
}
