#include <pybind11/pybind11.h>

#include "block.hpp"

namespace py = pybind11;

void init_java_block(py::module m_parent)
{
    auto m = m_parent.def_submodule("_block");
    std::string module_name = m.attr("__name__").cast<std::string>();

    py::enum_<Amulet::game::Waterloggable> Waterloggable(m, "Waterloggable");
    Waterloggable.value(
        "No",
        Amulet::game::Waterloggable::No,
        "Cannot be waterlogged.");
    Waterloggable.value(
        "Yes",
        Amulet::game::Waterloggable::Yes,
        "Can be waterlogged.");
    Waterloggable.value(
        "Always",
        Amulet::game::Waterloggable::Always,
        "Is always waterlogged. (attribute is not stored)");
    Waterloggable.attr("__repr__") = py::cpp_function(
        [module_name, Waterloggable](const py::object& arg) -> py::str {
            return py::str("{}.{}").format(module_name, Waterloggable.attr("__str__")(arg));
        },
        py::name("__repr__"),
        py::is_method(Waterloggable));
}
