#pragma once

#include <X11/Xlib.h>

#include <memory>
#include <vector>

#include "../core/finder.h"
#include "../core/window.h"

namespace appwindows {
namespace x_server {

class FinderXServer final : public core::Finder {
 public:
  FinderXServer();
  [[nodiscard]]
  std::shared_ptr<core::Window> get_window_by_title(
      std::string title) const override;
  [[nodiscard]]
  std::vector<std::shared_ptr<core::Window>> get_all_windows() const override;

  static Display* open_display();
};

}  // namespace x_server
}  // namespace appwindows
