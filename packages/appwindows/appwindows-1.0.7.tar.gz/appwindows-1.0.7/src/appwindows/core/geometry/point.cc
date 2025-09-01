#include "point.h"

#include <stdexcept>

namespace appwindows {
namespace core {

Point::Point(const int x, const int y) : x_(x), y_(y) {}

Point Point::operator+(const Point& other) const{
  return Point{x_ + other.get_x(), y_ + other.get_y()};
}

Point Point::operator-(const Point& other) const{
  return Point{x_ - other.get_x(), y_ - other.get_y()};
}

Point Point::operator/(const Point& other) const {
  if (other.get_x() == 0 || other.get_y() == 0) {
    throw std::invalid_argument("Division by zero in Point coordinates");
  }
  return Point{x_ / other.get_x(), y_ / other.get_y()};
}

Point Point::operator*(const Point& other) const{
  return Point{x_ * other.get_x(), y_ * other.get_y()};
}

int Point::get_x() const { return x_; }

int Point::get_y() const { return y_; }

}  // namespace core
}  // namespace appwindows