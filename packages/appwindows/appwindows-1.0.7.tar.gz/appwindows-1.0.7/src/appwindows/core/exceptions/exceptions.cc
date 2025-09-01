#include <pybind11/pybind11.h>

#include "invalid_size.h"
#include "window_does_not_exist.h"

namespace py = pybind11;

PYBIND11_MODULE(exceptions, m) {
  py::register_exception<appwindows::core::exceptions::InvalidSizeException>(m, "InvalidSizeException");
  py::register_exception<appwindows::core::exceptions::WindowDoesNotExistException>(m, "WindowDoesNotExistException");
}