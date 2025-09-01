#include "platform.h"

#ifdef WINDOWS_USED
#include "../windows/finder.h"
#elif X_SERVER_USED
#include "../x_server/finder.h"
#endif

namespace appwindows {
std::shared_ptr<core::Finder> get_finder() {
#ifdef WINDOWS_USED
  return std::make_shared<windows::FinderWindows>();
#elif X_SERVER_USED
  return std::make_shared<x_server::FinderXServer>();
#else
#error "Unsoported platform"
#endif
}

}  // namespace appwindows