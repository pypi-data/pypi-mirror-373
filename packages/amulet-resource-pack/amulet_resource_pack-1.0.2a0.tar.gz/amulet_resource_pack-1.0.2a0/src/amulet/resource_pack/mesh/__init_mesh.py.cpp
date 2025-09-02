#include <pybind11/pybind11.h>

#include <amulet/pybind11_extensions/py_module.hpp>

namespace py = pybind11;

void init_mesh_block(py::module m_parent);

void init_mesh(py::module m_parent)
{
    auto m = Amulet::pybind11_extensions::def_subpackage(m_parent, "mesh");
    init_mesh_block(m);
}
