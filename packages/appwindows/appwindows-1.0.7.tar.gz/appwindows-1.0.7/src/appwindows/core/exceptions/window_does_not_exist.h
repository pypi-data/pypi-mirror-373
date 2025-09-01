#pragma once

#include <stdexcept>

namespace appwindows {
namespace core {
namespace exceptions {

class WindowDoesNotExistException final : public std::runtime_error {
 public:
  explicit WindowDoesNotExistException()
      : runtime_error("Window does not exist") {}
};

}  // namespace exceptions
}  // namespace core
}  // namespace appwindows