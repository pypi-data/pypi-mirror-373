#include <functional>
#include <list>
#include <mutex>
#include <stdexcept>

#include "progress_manager.hpp"

namespace Amulet {

VoidProgressManager::VoidProgressManager() = default;
VoidProgressManager::~VoidProgressManager() = default;

VoidProgressManager::VoidProgressManager(const VoidProgressManager&) = default;
VoidProgressManager::VoidProgressManager(VoidProgressManager&&) = default;
VoidProgressManager& VoidProgressManager::operator=(const VoidProgressManager&) = default;
VoidProgressManager& VoidProgressManager::operator=(VoidProgressManager&&) = default;

EventToken<float> VoidProgressManager::register_progress_callback(ProgressCallback callback) { return {}; }
void VoidProgressManager::unregister_progress_callback(EventToken<float> token) { }
void VoidProgressManager::update_progress(float progress) { }
EventToken<std::string> VoidProgressManager::register_progress_text_callback(ProgressTextCallback callback) { return {}; }
void VoidProgressManager::unregister_progress_text_callback(EventToken<std::string> token) { }
void VoidProgressManager::update_progress_text(const std::string& text) { }
std::unique_ptr<AbstractProgressManager> VoidProgressManager::get_child(float progress_min, float progress_max)
{
    return std::make_unique<VoidProgressManager>(*this);
}

ProgressManager::ProgressManager(const std::shared_ptr<ProgressManagerData>& data, float progress_min, float progress_max)
    : data(data)
    , _progress_min(progress_min)
    , _progress_max(progress_max)
{
}

ProgressManager::ProgressManager()
    : ProgressManager(std::make_shared<ProgressManagerData>(), 0.0, 1.0)
{
}

ProgressManager::~ProgressManager() = default;

EventToken<float> ProgressManager::register_progress_callback(ProgressCallback callback)
{
    return data->progress_changed.connect(callback);
}

void ProgressManager::unregister_progress_callback(EventToken<float> token)
{
    data->progress_changed.disconnect(token);
}

void ProgressManager::update_progress(float progress)
{
    if (progress < 0.0 || 1.0 < progress) {
        throw std::invalid_argument("progress must be between 0.0 and 1.0");
    }
    data->progress_changed.dispatch(_progress_min + progress * (_progress_max - _progress_min));
}

EventToken<std::string> ProgressManager::register_progress_text_callback(ProgressTextCallback callback)
{
    return data->progress_text_changed.connect(callback);
}

void ProgressManager::unregister_progress_text_callback(EventToken<std::string> token)
{
    data->progress_text_changed.disconnect(token);
}

void ProgressManager::update_progress_text(const std::string& text)
{
    data->progress_text_changed.dispatch(text);
}

std::unique_ptr<AbstractProgressManager> ProgressManager::get_child(
    float progress_min, float progress_max)
{
    if (progress_min < 0.0 || progress_max < progress_min || 1.0 < progress_max) {
        throw std::invalid_argument("Invalid progress values. 0.0 <= progress_min <= progress_max <= 1.0");
    }
    return std::make_unique<ProgressManager>(
        data,
        _progress_min + progress_min * (_progress_max - _progress_min),
        _progress_min + progress_max * (_progress_max - _progress_min));
}

} // namespace Amulet
