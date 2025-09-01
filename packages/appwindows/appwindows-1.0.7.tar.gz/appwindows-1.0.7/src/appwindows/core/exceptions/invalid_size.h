#pragma once

#include <stdexcept>
#include <string>

namespace appwindows {
namespace core {
namespace exceptions {

class InvalidSizeException final : public std::invalid_argument {
 public:
  explicit InvalidSizeException(const int width, const int height)
      : invalid_argument("Invalid width(" + std::to_string(width) +
                         ") or height(" + std::to_string(height) + ")") {}
};

}  // namespace exceptions
}  // namespace core
}  // namespace appwindows