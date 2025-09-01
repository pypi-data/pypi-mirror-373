#pragma once

#ifndef AMULET_UTILS_EXPORT
    #if defined(WIN32) || defined(_WIN32)
        #ifdef ExportAmuletUtils
            #define AMULET_UTILS_EXPORT __declspec(dllexport)
        #else
            #define AMULET_UTILS_EXPORT __declspec(dllimport)
        #endif
    #else
        #define AMULET_UTILS_EXPORT
    #endif
#endif

#if !defined(AMULET_UTILS_EXPORT_EXCEPTION)
    #if defined(_LIBCPP_EXCEPTION)
        #define AMULET_UTILS_EXPORT_EXCEPTION __attribute__((visibility("default")))
    #else
        #define AMULET_UTILS_EXPORT_EXCEPTION
    #endif
#endif
