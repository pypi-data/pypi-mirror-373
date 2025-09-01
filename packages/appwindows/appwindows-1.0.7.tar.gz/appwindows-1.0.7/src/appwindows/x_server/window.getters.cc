#include "window.h"

#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <pybind11/numpy.h>

#include <memory>
#include <string>
#include <vector>

#include "../core/geometry/point.h"
#include "../core/geometry/size.h"
#include "finder.h"

namespace py = pybind11;

namespace appwindows {
namespace x_server {

std::unique_ptr<std::vector<core::Point>> WindowXServer::get_points() {
  XWindowAttributes attrs;
  auto display = FinderXServer::open_display();
  if (!XGetWindowAttributes(display, window_, &attrs)) return nullptr;
  auto points = std::make_unique<std::vector<core::Point>>();
  points->push_back({attrs.x, attrs.y});
  points->push_back({attrs.x + attrs.width, attrs.y});
  points->push_back({attrs.x + attrs.width, attrs.y + attrs.height});
  points->push_back({attrs.x, attrs.y + attrs.height});
  XCloseDisplay(display);
  return points;
}

std::unique_ptr<core::Size> WindowXServer::get_size() const {
  auto display = FinderXServer::open_display();
  XWindowAttributes attrs;
  if (!XGetWindowAttributes(display, window_, &attrs)) return nullptr;
  XCloseDisplay(display);
  return std::make_unique<core::Size>(attrs.width, attrs.height);
}

std::unique_ptr<std::string> WindowXServer::get_title() const {
  auto display = FinderXServer::open_display();
  Atom utf8_string = XInternAtom(display, "UTF8_STRING", False);
  Atom net_wm_name = XInternAtom(display, "_NET_WM_NAME", False);
  Atom actual_type;
  int actual_format;
  unsigned long nitems, bytes_after;
  unsigned char* data = nullptr;
  XGetWindowProperty(display, window_, net_wm_name, 0, (~0L), False,
                     utf8_string, &actual_type, &actual_format, &nitems,
                     &bytes_after, &data) == Success&& data;
  std::string title(reinterpret_cast<char*>(data), nitems);
  XFree(data);
  XCloseDisplay(display);
  return std::make_unique<std::string>(title);
}

py::array_t<unsigned char> WindowXServer::get_screenshot() {
  auto display = FinderXServer::open_display();
  auto size = get_size();
  auto image = XGetImage(display, window_, 0, 0, size->get_width(),
                         size->get_height(), AllPlanes, ZPixmap);
  std::vector<size_t> shape = {static_cast<size_t>(size->get_height()),
                               static_cast<size_t>(size->get_width()), 3};
  py::array_t<unsigned char> result(shape);
  auto buf = result.mutable_unchecked<3>();
  for (int y = 0; y < size->get_height(); ++y)
    for (int x = 0; x < size->get_width(); ++x) {
      unsigned long pixel = XGetPixel(image, x, y);
      buf(y, x, 0) = (pixel >> 16) & 0xff;
      buf(y, x, 1) = (pixel >> 8) & 0xff;
      buf(y, x, 2) = pixel & 0xff;
    }
  XDestroyImage(image);
  XCloseDisplay(display);
  return result;
}

}  // namespace x_server
}  // namespace appwindows
