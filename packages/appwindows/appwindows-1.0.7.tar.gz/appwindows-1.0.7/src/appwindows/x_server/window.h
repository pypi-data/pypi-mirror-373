#pragma once

#include <X11/Xlib.h>

#include <memory>
#include <vector>

#include "../core/window.h"

using WindowX = Window;

namespace appwindows {
namespace x_server {

class WindowXServer final : public core::Window {
 public:
  explicit WindowXServer(WindowX window);
  std::unique_ptr<std::vector<core::Point>> get_points() override;
  std::unique_ptr<core::Size> get_size() const override;
  std::unique_ptr<std::string> get_title() const override;
  py::array_t<unsigned char> get_screenshot() override;

  void set_minimize(bool is_minimize) override;
  void set_fullscreen(bool is_fullscreen) override;
  void resize(core::Size size) override;
  void move(core::Point point) override;
  void close() override;
  void to_foreground() override;
  void to_background() override;

 private:
  void to_background(bool is_background);
  void to_foreground(bool is_foreground);
  WindowX window_;
};

}  // namespace x_server
}  // namespace appwindows
