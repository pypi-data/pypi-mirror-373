#include "size.h"

#include "../exceptions/invalid_size.h"

namespace appwindows {
namespace core {

Size::Size(const int width, const int height) : width_(width), height_(height) {
  if (width <= 0) throw exceptions::InvalidSizeException(width, height);
  if (height <= 0) throw exceptions::InvalidSizeException(width, height);
}

}  // namespace core
}  // namespace appwindows