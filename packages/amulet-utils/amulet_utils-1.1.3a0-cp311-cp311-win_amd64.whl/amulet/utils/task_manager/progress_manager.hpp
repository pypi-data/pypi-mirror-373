#pragma once

#include <functional>
#include <list>
#include <memory>
#include <mutex>
#include <stdexcept>

#include <amulet/utils/dll.hpp>
#include <amulet/utils/event/event.hpp>

namespace Amulet {

using ProgressCallback = std::function<void(float)>;
using ProgressTextCallback = std::function<void(const std::string&)>;

class AbstractProgressManager {
public:
    AbstractProgressManager() = default;

    AbstractProgressManager(const AbstractProgressManager&) = default;
    AbstractProgressManager(AbstractProgressManager&&) = default;
    AbstractProgressManager& operator=(const AbstractProgressManager&) = default;
    AbstractProgressManager& operator=(AbstractProgressManager&&) = default;

    virtual ~AbstractProgressManager() = default;

    // Register a function to get called when progress changes.
    // The callback will be called from the thread `update_progress` is called in.
    // Thread safe.
    virtual EventToken<float> register_progress_callback(ProgressCallback callback) = 0;

    // Unregister a registered function from being called when update_progress is called.
    // Thread safe.
    virtual void unregister_progress_callback(EventToken<float> token) = 0;

    // Notify the caller of the updated progress.
    // progress must be in the range 0.0 - 1.0
    // Thread safe.
    virtual void update_progress(float progress) = 0;

    // Register a function to get called when progress changes.
    // The callback will be called from the thread `update_progress` is called in.
    // Thread safe.
    virtual EventToken<std::string> register_progress_text_callback(ProgressTextCallback callback) = 0;

    // Unregister a registered function from being called when update_progress is called.
    // Thread safe.
    virtual void unregister_progress_text_callback(EventToken<std::string> token) = 0;

    // Send a new progress text to the caller.
    // Thread safe.
    virtual void update_progress_text(const std::string& text) = 0;

    // Get a child ProgressManager.
    // If calling multiple functions, this allows segmenting the reported time.
    // Thread safe.
    virtual std::unique_ptr<AbstractProgressManager> get_child(
        float progress_min, float progress_max)
        = 0;
};

class VoidProgressManager : public AbstractProgressManager {
public:
    AMULET_UTILS_EXPORT VoidProgressManager();

    AMULET_UTILS_EXPORT VoidProgressManager(const VoidProgressManager&);
    AMULET_UTILS_EXPORT VoidProgressManager(VoidProgressManager&&);
    AMULET_UTILS_EXPORT VoidProgressManager& operator=(const VoidProgressManager&);
    AMULET_UTILS_EXPORT VoidProgressManager& operator=(VoidProgressManager&&);

    AMULET_UTILS_EXPORT ~VoidProgressManager() override;

    AMULET_UTILS_EXPORT EventToken<float> register_progress_callback(ProgressCallback callback) override;
    AMULET_UTILS_EXPORT void unregister_progress_callback(EventToken<float> token) override;
    AMULET_UTILS_EXPORT void update_progress(float progress) override;
    AMULET_UTILS_EXPORT EventToken<std::string> register_progress_text_callback(ProgressTextCallback callback) override;
    AMULET_UTILS_EXPORT void unregister_progress_text_callback(EventToken<std::string> token) override;
    AMULET_UTILS_EXPORT void update_progress_text(const std::string& text) override;
    AMULET_UTILS_EXPORT std::unique_ptr<AbstractProgressManager> get_child(
        float progress_min, float progress_max) override;
};

class ProgressManagerData {
public:
    Event<float> progress_changed;
    Event<std::string> progress_text_changed;
};

class ProgressManager : public AbstractProgressManager {
private:
    std::shared_ptr<ProgressManagerData> data;
    float _progress_min;
    float _progress_max;

public:
    AMULET_UTILS_EXPORT ProgressManager(const std::shared_ptr<ProgressManagerData>& data, float progress_min, float progress_max);
    AMULET_UTILS_EXPORT ProgressManager();

    ProgressManager(const ProgressManager&) = delete;
    ProgressManager(ProgressManager&&) = delete;
    ProgressManager& operator=(const ProgressManager&) = delete;
    ProgressManager& operator=(ProgressManager&&) = delete;

    AMULET_UTILS_EXPORT ~ProgressManager() override;

    AMULET_UTILS_EXPORT EventToken<float> register_progress_callback(ProgressCallback callback) override;
    AMULET_UTILS_EXPORT void unregister_progress_callback(EventToken<float> token) override;
    AMULET_UTILS_EXPORT void update_progress(float progress) override;
    AMULET_UTILS_EXPORT EventToken<std::string> register_progress_text_callback(ProgressTextCallback callback) override;
    AMULET_UTILS_EXPORT void unregister_progress_text_callback(EventToken<std::string> token) override;
    AMULET_UTILS_EXPORT void update_progress_text(const std::string& text) override;
    AMULET_UTILS_EXPORT std::unique_ptr<AbstractProgressManager> get_child(
        float progress_min, float progress_max) override;
};

} // namespace Amulet
