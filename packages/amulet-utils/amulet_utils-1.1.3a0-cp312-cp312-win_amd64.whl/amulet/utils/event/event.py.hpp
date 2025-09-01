#pragma once

#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/typing.h>

#include <memory>

#include <amulet/pybind11_extensions/nogil_holder.hpp>
#include <amulet/pybind11_extensions/pybind11.hpp>

#include <amulet/utils/python.hpp>

#include "event.hpp"

namespace py = pybind11;
namespace pyext = Amulet::pybind11_extensions;

namespace Amulet {

template <typename... Args>
class PyEvent : public py::object {
    PYBIND11_OBJECT_DEFAULT(PyEvent, object, PyObject_Type)
    using object::object;
};

template <typename... Args>
class PyEventToken : public py::object {
    PYBIND11_OBJECT_DEFAULT(PyEventToken, object, PyObject_Type)
    using object::object;
};

// Create a python binding for the event class.
template <typename eventT>
void create_event_binding()
{
    if (!pyext::is_class_bound<eventT>()) {
        pybind11::class_<typename eventT::tokenT>(pybind11::handle(), "EventToken", pybind11::module_local());

        pybind11::class_<eventT, pyext::nogil_shared_ptr<eventT>>(pybind11::handle(), "Event", pybind11::module_local())
            .def(
                "connect",
                [](eventT& self, typename eventT::callbackT callback, ConnectionMode mode) {
                    // Bad things happen if this is called after python shuts down.
                    // Add a wrapper to make sure python is still running.
                    auto py_valid = get_py_valid();
                    auto callback_wrapper = [callback, py_valid](auto... args) {
                        if (*py_valid) {
                            callback(args...);
                        } else {
                            throw std::runtime_error(
                                "Cannot execute Python function connected to Event because the Python interpreter has been shut down. "
                                "Python callbacks must be disconnected before the interpreter shuts down.");
                        }
                    };
                    py::gil_scoped_release nogil;
                    return self.connect(callback_wrapper, mode);
                },
                py::arg("callback"),
                py::arg("mode") = Amulet::ConnectionMode::Direct)
            .def("disconnect", &eventT::disconnect, py::call_guard<py::gil_scoped_release>())
            .def("dispatch", &eventT::dispatch, py::call_guard<py::gil_scoped_release>());
    }
}

// Define an event getter on a class.
// This automatically creates the binding class.
template <typename PyCls, typename CppCls, typename... Args, typename... Extra>
void def_event(PyCls& cls, const char* name, const Event<Args...> CppCls::*attr, const Extra&... extra)
{
    create_event_binding<Event<Args...>>();
    cls.def_property_readonly(
        name,
        py::cpp_function(
            [attr](const typename PyCls::type& self) -> PyEvent<Args...> {
                return pybind11::cast(self.*attr, py::return_value_policy::reference);
            },
            py::keep_alive<0, 1>()),
        extra...);
}

};

namespace pybind11 {
namespace detail {
    namespace {

        template <typename T, typename... Ts>
        constexpr auto get_args_str()
        {
            if constexpr ((sizeof...(Ts)) == 0) {
                return make_caster<T>::name;
            } else {
                return make_caster<T>::name + ((const_name(", ") + make_caster<Ts>::name) + ...);
            }
        }

    }

    template <>
    struct handle_type_name<Amulet::PyEvent<>> {
        static constexpr auto name = const_name("amulet.utils.event.Event[()]");
    };

    template <typename T, typename... Ts>
    struct handle_type_name<Amulet::PyEvent<T, Ts...>> {
        static constexpr auto name = const_name("amulet.utils.event.Event[") + get_args_str<T, Ts...>() + const_name("]");
    };

    template <>
    struct handle_type_name<Amulet::PyEventToken<>> {
        static constexpr auto name = const_name("amulet.utils.event.EventToken[()]");
    };

    template <typename T, typename... Ts>
    struct handle_type_name<Amulet::PyEventToken<T, Ts...>> {
        static constexpr auto name = const_name("amulet.utils.event.EventToken[") + get_args_str<T, Ts...>() + const_name("]");
    };
}
}
