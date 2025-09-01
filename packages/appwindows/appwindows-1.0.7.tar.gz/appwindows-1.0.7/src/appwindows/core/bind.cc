#include "bind.h"

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "finder.h"
#include "window.h"

namespace py = pybind11;

namespace appwindows {
namespace core {

void bind_window(py::module &m) {
  py::class_<Window, std::shared_ptr<Window>>(
      m, "Window", "Interface representing an application window")
      .def(
          "get_points",
          [](Window &self) {
            auto points = self.get_points();
            return points ? *points : std::vector<Point>{};
          },
          "Get all points associated with the window\n"
          ""
          "Returns:\n"
          "    list[Point]: List of points")
      .def(
          "get_title",
          [](const Window &self) {
            const auto title = self.get_title();
            return title ? *title : std::string{};
          },
          "Get the window title\n\n"
          "Returns:\n"
          "    str: Window title")
      .def(
          "get_size",
          [](const Window &self) {
            auto size = self.get_size();
            return size ? *size : Size{0, 0};
          },
          "Get current window size\n\n"
          "Returns:\n"
          "    Size: Current window dimensions")
      .def(
          "get_screenshot",
          [](Window &self) {return self.get_screenshot();},
          "Get current window image\n\n"
          "Returns:\n"
          "    ndarray: image in ndarray")
      .def("to_foreground", &Window::to_foreground, "Moved window to forground")
      .def("to_background", &Window::to_background,
           "Moved window to background")
      .def("set_minimize", &Window::set_minimize,
           "Set window active state\n\n"
           "Args:\n"
           "    is_minimize (bool): True to activate window",
           py::arg("is_minimize"))
      .def("set_fullscreen", &Window::set_fullscreen,
           "Maximize or restore the window\n\n"
           "Args:\n"
           "    is_fullscreen (bool): True to window on fullscreen",
           py::arg("is_maximize"))
      .def("resize", &Window::resize,
           "Resize the window\n\n"
           "Args:\n"
           "    size (appwindows.geometry.Size): New window dimensions\n\n"
           "Raises:\n"
           "    InvalidSizeError: If size is invalid",
           py::arg("size"))
      .def("move", &Window::move,
           "Move window to specified position\n\n"
           "Args:\n"
           "    point (appwindows.geometry.Point): New window position",
           py::arg("point"))
      .def("close", &Window::close, "Close the window");
}

void bind_finder(py::module &m) {
  py::class_<Finder, std::shared_ptr<Finder>>(
      m, "Finder", "Interface for finding application windows")
      .def(
          "get_window_by_title",
          [](const Finder &self, const std::string &title) {
            return self.get_window_by_title(title);
          },
          "Find window by its title substring\n\n"
          "Args:\n"
          "    title (str): Window title to search for\n\n"
          "Returns:\n"
          "    Window | None: Found window or null if window does not exist",
          py::arg("title"))
      .def(
          "get_all_windows",
          [](const Finder &self) { return self.get_all_windows(); },
          "Find all opened windows\n\n"
          "Returns:\n"
          "    list[Window]: Found windows\n\n");
}

}  // namespace core
}  // namespace appwindows
