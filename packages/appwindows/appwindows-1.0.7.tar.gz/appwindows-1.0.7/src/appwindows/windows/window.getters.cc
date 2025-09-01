#include "window.h"

#ifndef PW_RENDERFULLCONTENT
#define PW_RENDERFULLCONTENT 0x00000002
#endif

#include <windows.h>

#include "../core/exceptions/window_does_not_exist.h"

namespace appwindows {
namespace windows {

std::unique_ptr<std::string> WindowWindows::get_title() const {
  if (!window_is_valid()) throw core::exceptions::WindowDoesNotExistException();
  const int length = GetWindowTextLengthW(*window_);
  if (length == 0) return std::make_unique<std::string>("");
  std::wstring wide_title(length + 1, L'\0');
  GetWindowTextW(*window_, &wide_title[0], length + 1);
  const int utf8_size = WideCharToMultiByte(CP_UTF8, 0, wide_title.c_str(), -1,
                                            nullptr, 0, nullptr, nullptr);
  if (utf8_size == 0) return std::make_unique<std::string>("");
  std::string utf8_title(utf8_size, '\0');
  WideCharToMultiByte(CP_UTF8, 0, wide_title.c_str(), -1, &utf8_title[0],
                      utf8_size, nullptr, nullptr);
  utf8_title.resize(utf8_size - 1);
  return std::make_unique<std::string>(std::move(utf8_title));
}

std::unique_ptr<std::vector<core::Point>> WindowWindows::get_points() {
  if (!window_is_valid()) throw core::exceptions::WindowDoesNotExistException();
  RECT rect;
  GetWindowRect(*window_, &rect);
  auto points = std::make_unique<std::vector<core::Point>>();
  points->reserve(4);
  points->emplace_back(static_cast<int>(rect.left), static_cast<int>(rect.top));
  points->emplace_back(static_cast<int>(rect.right),
                       static_cast<int>(rect.top));
  points->emplace_back(static_cast<int>(rect.right),
                       static_cast<int>(rect.bottom));
  points->emplace_back(static_cast<int>(rect.left),
                       static_cast<int>(rect.bottom));
  return points;
}

std::unique_ptr<core::Size> WindowWindows::get_size() const {
  if (!window_is_valid()) throw core::exceptions::WindowDoesNotExistException();
  RECT rect = {0};
  GetWindowRect(*window_, &rect);
  return std::make_unique<core::Size>(rect.right - rect.left,
                                      rect.bottom - rect.top);
}

py::array_t<unsigned char> WindowWindows::get_screenshot() {
  if (!window_is_valid()) throw core::exceptions::WindowDoesNotExistException();
  const auto is_minimize = IsIconic(*window_) == TRUE;
  if (is_minimize) {
    ShowWindow(*window_, SW_SHOWNOACTIVATE);
    Sleep(50);
  }
  const auto window_size = get_size();
  const auto width = window_size->get_width();
  const auto height = window_size->get_height();
  const auto window_dc = GetWindowDC(*window_);
  const auto memory_dc = CreateCompatibleDC(window_dc);
  const auto bitmap = CreateCompatibleBitmap(window_dc, width, height);
  const auto old_bitmap = SelectObject(memory_dc, bitmap);
  PrintWindow(*window_, memory_dc, PW_RENDERFULLCONTENT);
  BITMAPINFOHEADER bitmap_info = {};
  bitmap_info.biSize = sizeof(BITMAPINFOHEADER);
  bitmap_info.biWidth = width;
  bitmap_info.biHeight = -height;
  bitmap_info.biPlanes = 1;
  bitmap_info.biBitCount = 32;
  bitmap_info.biCompression = BI_RGB;
  const auto pixel_buffer =
      std::make_unique<unsigned char[]>(width * height * 4);
  GetDIBits(memory_dc, bitmap, 0, height, pixel_buffer.get(),
            reinterpret_cast<BITMAPINFO*>(&bitmap_info), DIB_RGB_COLORS);
  SelectObject(memory_dc, old_bitmap);
  DeleteObject(bitmap);
  DeleteDC(memory_dc);
  ReleaseDC(*window_, window_dc);
  if (is_minimize) set_minimize(true);
  auto result_array = py::array_t<unsigned char>({height, width, 3});
  auto array_data = result_array.mutable_unchecked<3>();
  for (int y = 0; y < height; ++y)
    for (int x = 0; x < width; ++x) {
      const size_t buffer_index = (y * width + x) * 4;
      array_data(y, x, 0) = pixel_buffer[buffer_index + 2];
      array_data(y, x, 1) = pixel_buffer[buffer_index + 1];
      array_data(y, x, 2) = pixel_buffer[buffer_index];
    }
  return result_array;
}

}  // namespace windows
}  // namespace appwindows
