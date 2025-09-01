#include "finder.h"

#include <windows.h>

#include <memory>

#include "../core/window.h"
#include "exceptions/invalid_size.h"
#include "exceptions/window_does_not_exist.h"
#include "window.h"

namespace appwindows {
namespace windows {

FinderWindows::FinderWindows() = default;

std::shared_ptr<core::Window> FinderWindows::get_window_by_title(
    const std::string title) const {
  const auto windows = FinderWindows::get_all_windows();
  for (auto window : windows)
    if (window->get_title()->find(title) != std::string::npos) return window;
  throw core::exceptions::WindowDoesNotExistException();
}

std::vector<std::shared_ptr<core::Window>> FinderWindows::get_all_windows()
    const {
  std::vector<std::shared_ptr<core::Window>> result;
  EnumWindows(
      [](const HWND hwnd, const LPARAM lparam) {
        auto& windows =
            *reinterpret_cast<std::vector<std::shared_ptr<core::Window>>*>(
                lparam);
        if (IsWindowVisible(hwnd))
          windows.push_back(
              std::make_shared<WindowWindows>(std::make_shared<HWND>(hwnd)));
        return TRUE;
      },
      reinterpret_cast<LPARAM>(&result));
  return result;
}

}  // namespace windows
}  // namespace appwindows