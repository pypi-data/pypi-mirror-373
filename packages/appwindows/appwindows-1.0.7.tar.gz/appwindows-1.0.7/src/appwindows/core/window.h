#pragma once

#include <memory>
#include <string>
#include <vector>

#include <pybind11/numpy.h>

#include "geometry/point.h"
#include "geometry/size.h"

namespace py = pybind11;

namespace appwindows {
namespace core {

class Window {
 public:
  virtual ~Window() = default;
  virtual std::unique_ptr<std::vector<Point>> get_points() = 0;
  [[nodiscard]] virtual std::unique_ptr<std::string> get_title() const = 0;
  [[nodiscard]] virtual std::unique_ptr<Size> get_size() const = 0;
  [[nodiscard]] virtual py::array_t<unsigned char> get_screenshot() = 0;
  
  virtual void set_minimize(bool is_minimize) = 0;
  virtual void set_fullscreen(bool is_fullscreen) = 0;
  virtual void resize(Size size) = 0;
  virtual void move(Point point) = 0;
  virtual void close() = 0;
  virtual void to_foreground() = 0;
  virtual void to_background() = 0;
};

}  // namespace core
}  // namespace appwindows
