if (NOT TARGET amulet_game)
    message(STATUS "Finding amulet_game")

    find_package(pybind11 CONFIG REQUIRED)
    find_package(amulet_io CONFIG REQUIRED)
    find_package(amulet_nbt CONFIG REQUIRED)
    find_package(amulet_core CONFIG REQUIRED)

    set(amulet_game_INCLUDE_DIR "${CMAKE_CURRENT_LIST_DIR}/../..")
    find_library(amulet_game_LIBRARY NAMES amulet_game PATHS "${CMAKE_CURRENT_LIST_DIR}")
    message(STATUS "amulet_game_LIBRARY: ${amulet_game_LIBRARY}")

    add_library(amulet_game_bin SHARED IMPORTED)
    set_target_properties(amulet_game_bin PROPERTIES
        IMPORTED_IMPLIB "${amulet_game_LIBRARY}"
    )

    add_library(amulet_game INTERFACE)
    target_link_libraries(amulet_game INTERFACE pybind11::module)
    target_link_libraries(amulet_game INTERFACE amulet_io)
    target_link_libraries(amulet_game INTERFACE amulet_nbt)
    target_link_libraries(amulet_game INTERFACE amulet_core)
    target_link_libraries(amulet_game INTERFACE amulet_game_bin)
    target_include_directories(amulet_game INTERFACE ${amulet_game_INCLUDE_DIR})
endif()
