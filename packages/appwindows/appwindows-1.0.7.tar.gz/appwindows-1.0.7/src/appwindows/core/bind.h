#pragma once

#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace appwindows {
namespace core {

void bind_window(py::module &m);
void bind_finder(py::module &m);

}  // namespace windows
}  // namespace appwindows
