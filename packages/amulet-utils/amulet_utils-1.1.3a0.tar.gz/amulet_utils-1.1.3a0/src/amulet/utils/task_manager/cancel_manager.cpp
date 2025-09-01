#include <functional>
#include <list>
#include <memory>
#include <mutex>
#include <stdexcept>

#include "cancel_manager.hpp"
#include <amulet/utils/logging/logging.hpp>

namespace Amulet {

// VoidCancelManager
VoidCancelManager::VoidCancelManager() = default;
VoidCancelManager::VoidCancelManager(const VoidCancelManager&) = default;
VoidCancelManager::VoidCancelManager(VoidCancelManager&&) = default;
VoidCancelManager& VoidCancelManager::operator=(const VoidCancelManager&) = default;
VoidCancelManager& VoidCancelManager::operator=(VoidCancelManager&&) = default;
VoidCancelManager::~VoidCancelManager() = default;
void VoidCancelManager::cancel() { }
bool VoidCancelManager::is_cancel_requested() { return false; }
EventToken<> VoidCancelManager::register_cancel_callback(CancelCallback callback)
{
    // Construct an empty token to keep the API consistent.
    return {};
}
void VoidCancelManager::unregister_cancel_callback(EventToken<> token) { }

VoidCancelManager global_VoidCancelManager;

// CancelManager
CancelManager::CancelManager() = default;
CancelManager::~CancelManager() = default;

void CancelManager::cancel()
{
    {
        std::lock_guard lock(mutex);
        if (cancelled) {
            return;
        }
        cancelled = true;
    }
    event.dispatch();
}
bool CancelManager::is_cancel_requested()
{
    return cancelled;
}
EventToken<> CancelManager::register_cancel_callback(CancelCallback callback)
{
    return event.connect(callback);
}
void CancelManager::unregister_cancel_callback(EventToken<> token)
{
    event.disconnect(token);
}

} // namespace Amulet
