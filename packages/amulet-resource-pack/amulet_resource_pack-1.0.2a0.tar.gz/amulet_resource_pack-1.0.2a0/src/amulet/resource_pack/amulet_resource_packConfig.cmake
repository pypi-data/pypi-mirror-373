if (NOT TARGET amulet_resource_pack)
    message(STATUS "Finding amulet_resource_pack")

    find_package(amulet_utils CONFIG REQUIRED)
    find_package(amulet_core CONFIG REQUIRED)

    set(amulet_resource_pack_INCLUDE_DIR "${CMAKE_CURRENT_LIST_DIR}/../..")
    find_library(amulet_resource_pack_LIBRARY NAMES amulet_resource_pack PATHS "${CMAKE_CURRENT_LIST_DIR}")
    message(STATUS "amulet_resource_pack_LIBRARY: ${amulet_resource_pack_LIBRARY}")

    add_library(amulet_resource_pack_bin SHARED IMPORTED)
    set_target_properties(amulet_resource_pack_bin PROPERTIES
        IMPORTED_IMPLIB "${amulet_resource_pack_LIBRARY}"
    )

    add_library(amulet_resource_pack INTERFACE)
    target_link_libraries(amulet_resource_pack INTERFACE amulet_utils)
    target_link_libraries(amulet_resource_pack INTERFACE amulet_core)
    target_link_libraries(amulet_resource_pack INTERFACE amulet_resource_pack_bin)
    target_include_directories(amulet_resource_pack INTERFACE ${amulet_resource_pack_INCLUDE_DIR})
endif()
