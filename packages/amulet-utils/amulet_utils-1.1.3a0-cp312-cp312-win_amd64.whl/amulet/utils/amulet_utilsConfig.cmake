if (NOT TARGET amulet_utils)
    message(STATUS "Finding amulet_utils")

    find_package(pybind11 CONFIG REQUIRED)
    find_package(amulet_pybind11_extensions CONFIG REQUIRED)

    set(amulet_utils_INCLUDE_DIR "${CMAKE_CURRENT_LIST_DIR}/../..")
    find_library(amulet_utils_LIBRARY NAMES amulet_utils PATHS "${CMAKE_CURRENT_LIST_DIR}")
    message(STATUS "amulet_utils_LIBRARY: ${amulet_utils_LIBRARY}")

    add_library(amulet_utils_bin SHARED IMPORTED)
    set_target_properties(amulet_utils_bin PROPERTIES
        IMPORTED_IMPLIB "${amulet_utils_LIBRARY}"
    )

    add_library(amulet_utils INTERFACE)
    target_link_libraries(amulet_utils INTERFACE pybind11::module)
    target_link_libraries(amulet_utils INTERFACE amulet_pybind11_extensions)
    target_link_libraries(amulet_utils INTERFACE amulet_utils_bin)
    target_include_directories(amulet_utils INTERFACE ${amulet_utils_INCLUDE_DIR})
endif()
