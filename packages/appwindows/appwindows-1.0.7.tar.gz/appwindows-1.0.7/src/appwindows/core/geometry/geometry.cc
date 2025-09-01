#include <pybind11/pybind11.h>

#include "point.h"
#include "size.h"

namespace py = pybind11;

PYBIND11_MODULE(geometry, m) {
  py::class_<appwindows::core::Point>(
      m, "Point", "Represents a 2D point with x and y coordinates")
      .def(py::init<int, int>(),
           "Create a point with specified coordinates\n\n"
           "Args:\n"
           "    x (int): X coordinate\n"
           "    y (int): Y coordinate",
           py::arg("x"), py::arg("y"))
      .def("__add__", &appwindows::core::Point::operator+, "Add two points")
      .def("__sub__", &appwindows::core::Point::operator-,
           "Subtract two points")
      .def("__mul__", &appwindows::core::Point::operator*,
           "Multiply two points")
      .def("__truediv__", &appwindows::core::Point::operator/,
           "Divide two points")
      .def_property_readonly("x", &appwindows::core::Point::get_x,
                             "X coordinate")
      .def_property_readonly("y", &appwindows::core::Point::get_y,
                             "Y coordinate");

  py::class_<appwindows::core::Size>(
      m, "Size", "Represents dimensions with width and height")
      .def(py::init<int, int>(),
           "Create size with specified dimensions\n\n"
           "Args:\n"
           "    width (int): Width dimension\n"
           "    height (int): Height dimension\n\n"
           "Raises:\n"
           "    InvalidSizeError: If width or height are invalid",
           py::arg("width"), py::arg("height"))
      .def_property_readonly("width", &appwindows::core::Size::get_width,
                             "Width dimension")
      .def_property_readonly("height", &appwindows::core::Size::get_height,
                             "Height dimension");
}