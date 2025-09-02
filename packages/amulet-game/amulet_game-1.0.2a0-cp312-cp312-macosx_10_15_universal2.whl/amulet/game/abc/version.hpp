#pragma once

#include <pybind11/pybind11.h>

#include <memory>

#include "biome.hpp"
#include "block.hpp"

#include <amulet/game/dll.hpp>

#include <amulet/game/pyobj/wrapper.hpp>

namespace py = pybind11;

namespace Amulet {
namespace game {

    class GameVersionImpl;

    class GameVersion : public PyObjWrapper {
    public:
        using PyObjWrapper::PyObjWrapper;
        using PyObjWrapper::operator=;

        AMULET_GAME_EXPORT std::shared_ptr<BiomeData> get_biome_data();
        AMULET_GAME_EXPORT std::shared_ptr<BlockData> get_block_data();
    };

} // namespace game
} // namespace Amulet
