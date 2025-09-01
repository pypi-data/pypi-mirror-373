if (NOT TARGET amulet_zlib)
    message(STATUS "Finding amulet_zlib")

    set(amulet_zlib_INCLUDE_DIR "${CMAKE_CURRENT_LIST_DIR}/../..")
    find_library(amulet_zlib_LIBRARY NAMES amulet_zlib PATHS "${CMAKE_CURRENT_LIST_DIR}")
    message(STATUS "amulet_zlib_LIBRARY: ${amulet_zlib_LIBRARY}")

    add_library(amulet_zlib_bin SHARED IMPORTED)
    set_target_properties(amulet_zlib_bin PROPERTIES
        IMPORTED_IMPLIB "${amulet_zlib_LIBRARY}"
    )

    add_library(amulet_zlib INTERFACE)
    target_link_libraries(amulet_zlib INTERFACE amulet_zlib_bin)
    target_include_directories(amulet_zlib INTERFACE ${amulet_zlib_INCLUDE_DIR})
endif()
