#include <pybind11/pybind11.h>

#include <filesystem>

#include <amulet/pybind11_extensions/py_module.hpp>

#include "image.hpp"


namespace py = pybind11;

void init_image(py::module m_parent)
{
    auto m = Amulet::pybind11_extensions::def_subpackage(m_parent, "image");
    py::list __path__ = m.attr("__path__");
    std::filesystem::path path = __path__[0].cast<std::string>();
    
    m.def("get_missing_pack_icon", &Amulet::get_missing_pack_icon);

    m.attr("missing_pack_icon_path") = py::cast((path / "missing_pack.png").string());
}
