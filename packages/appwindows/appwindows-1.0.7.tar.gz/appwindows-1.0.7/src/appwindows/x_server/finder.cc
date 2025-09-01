#include "finder.h"

#include <X11/Xlib.h>
#include <X11/Xutil.h>

#include <memory>
#include <stdexcept>
#include <string>

#include "../core/window.h"
#include "../core/exceptions/invalid_size.h"
#include "../core/exceptions/window_does_not_exist.h"
#include "window.h"

using WIndowX = Window;

namespace appwindows {
namespace x_server {

FinderXServer::FinderXServer() = default;

Display* FinderXServer::open_display() {
  auto display = XOpenDisplay(nullptr);
  if (!display) throw std::runtime_error("Cannot open X11 display");
  return display;
}

std::shared_ptr<core::Window> FinderXServer::get_window_by_title(
    const std::string title) const {
  auto windows = FinderXServer::get_all_windows();
  for (auto window : windows)
    if (window->get_title() &&
        window->get_title()->find(title) != std::string::npos)
      return window;
  throw core::exceptions::WindowDoesNotExistException();
}

std::vector<std::shared_ptr<core::Window>> FinderXServer::get_all_windows()
    const {
  auto display = FinderXServer::open_display();
  std::vector<std::shared_ptr<core::Window>> windows;
  WindowX root = DefaultRootWindow(display);
  Atom net_wm_window_type = XInternAtom(display, "_NET_WM_WINDOW_TYPE", False);
  Atom net_wm_window_type_normal =
      XInternAtom(display, "_NET_WM_WINDOW_TYPE_NORMAL", False);
  Atom xa_atom = XInternAtom(display, "ATOM", False);
  WindowX* children = nullptr;
  unsigned int nchildren = 0;
  if (XQueryTree(display, root, &root, &root, &children, &nchildren)) {
    for (unsigned int i = 0; i < nchildren; ++i) {
      Atom type;
      int format;
      unsigned long nitems, bytes_after;
      unsigned char* data = nullptr;
      if (XGetWindowProperty(display, children[i], net_wm_window_type, 0, ~0L,
                             False, xa_atom, &type, &format, &nitems,
                             &bytes_after, &data) == Success) {
        if (type == xa_atom && data) {
          Atom* types = (Atom*)data;
          for (unsigned long j = 0; j < nitems; j++)
            if (types[j] == net_wm_window_type_normal) {
              windows.push_back(std::make_shared<WindowXServer>(children[i]));
              break;
            }
          XFree(data);
        }
      }
    }
    if (children) XFree(children);
  }
  XCloseDisplay(display);
  return windows;
}

}  // namespace x_server
}  // namespace appwindows
