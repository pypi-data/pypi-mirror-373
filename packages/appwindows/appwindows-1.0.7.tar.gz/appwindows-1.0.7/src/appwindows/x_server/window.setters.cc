#include "window.h"

#include <X11/Xlib.h>

#include <cstring>

#include "../core/geometry/point.h"
#include "../core/geometry/size.h"
#include "finder.h"

using WindowX = Window;

namespace appwindows {
namespace x_server {

WindowXServer::WindowXServer(const WindowX window) : window_(window) {}

void WindowXServer::to_foreground(const bool is_foreground) {
  auto display = FinderXServer::open_display();
  Atom wm_state = XInternAtom(display, "_NET_WM_STATE", False);
  Atom to_foreground = XInternAtom(display, "_NET_WM_STATE_ABOVE", False);
  XEvent event;
  memset(&event, 0, sizeof(event));
  event.type = ClientMessage;
  event.xclient.window = window_;
  event.xclient.message_type = wm_state;
  event.xclient.format = 32;
  event.xclient.data.l[0] = is_foreground ? 1 : 0;
  event.xclient.data.l[1] = to_foreground;
  XSendEvent(display, DefaultRootWindow(display), False,
             SubstructureRedirectMask | SubstructureNotifyMask, &event);
  XFlush(display);
  XCloseDisplay(display);
}

void WindowXServer::to_background(const bool is_background) {
  auto display = FinderXServer::open_display();
  Atom wm_state = XInternAtom(display, "_NET_WM_STATE", False);
  Atom to_background = XInternAtom(display, "_NET_WM_STATE_BELOW", False);
  XEvent event;
  memset(&event, 0, sizeof(event));
  event.type = ClientMessage;
  event.xclient.window = window_;
  event.xclient.message_type = wm_state;
  event.xclient.format = 32;
  event.xclient.data.l[0] = is_background ? 1 : 0;
  event.xclient.data.l[1] = to_background;
  XSendEvent(display, DefaultRootWindow(display), False,
             SubstructureRedirectMask | SubstructureNotifyMask, &event);
  XFlush(display);
  XCloseDisplay(display);
}

void WindowXServer::set_fullscreen(const bool is_fullscreen) {
  auto display = FinderXServer::open_display();
  Atom wm_state = XInternAtom(display, "_NET_WM_STATE", False);
  Atom fullscreen_atom =
      XInternAtom(display, "_NET_WM_STATE_FULLSCREEN", False);
  XEvent event;
  memset(&event, 0, sizeof(event));
  event.type = ClientMessage;
  event.xclient.window = window_;
  event.xclient.message_type = wm_state;
  event.xclient.format = 32;
  event.xclient.data.l[0] = is_fullscreen ? 1 : 0;
  event.xclient.data.l[1] = fullscreen_atom;
  XSendEvent(display, DefaultRootWindow(display), False,
             SubstructureRedirectMask | SubstructureNotifyMask, &event);
  XFlush(display);
  XCloseDisplay(display);
}

void WindowXServer::set_minimize(const bool is_minimize) {
  auto display = FinderXServer::open_display();
  Atom wm_state = XInternAtom(display, "_NET_WM_STATE", False);
  Atom hidden = XInternAtom(display, "_NET_WM_STATE_HIDDEN", False);
  XEvent event;
  std::memset(&event, 0, sizeof(event));
  event.type = ClientMessage;
  event.xclient.window = window_;
  event.xclient.message_type = wm_state;
  event.xclient.format = 32;
  event.xclient.data.l[0] = is_minimize ? 1 : 0;
  event.xclient.data.l[1] = hidden;
  XSendEvent(display, DefaultRootWindow(display), False,
             SubstructureRedirectMask | SubstructureNotifyMask, &event);
  XFlush(display);
  XCloseDisplay(display);
}

void WindowXServer::resize(const core::Size size) {
  auto display = FinderXServer::open_display();
  XResizeWindow(display, window_, size.get_width(), size.get_height());
  XFlush(display);
  XCloseDisplay(display);
}

void WindowXServer::move(const core::Point point) {
  auto display = FinderXServer::open_display();
  XMoveWindow(display, window_, point.get_x(), point.get_y());
  XFlush(display);
  XCloseDisplay(display);
}

void WindowXServer::close() {
  auto display = FinderXServer::open_display();
  XDestroyWindow(display, window_);
  XFlush(display);
  XCloseDisplay(display);
}

void WindowXServer::to_foreground() {
  to_foreground(true);
  to_background(false);
}

void WindowXServer::to_background() {
  to_background(true);
  to_foreground(false);
}

}  // namespace x_server
}  // namespace appwindows
