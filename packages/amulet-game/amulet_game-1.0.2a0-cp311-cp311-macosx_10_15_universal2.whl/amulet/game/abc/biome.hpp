#pragma once

#include <pybind11/pybind11.h>

#include <memory>

#include <amulet/core/biome/biome.hpp>

#include <amulet/game/dll.hpp>

#include <amulet/game/pyobj/wrapper.hpp>

namespace py = pybind11;

namespace Amulet {
namespace game {

    class BiomeData : public PyObjWrapper {
    public:
        using PyObjWrapper::PyObjWrapper;
        using PyObjWrapper::operator=;

        AMULET_GAME_EXPORT Biome translate(const std::string& platform, const VersionNumber& version, const Biome& biome);
    };

} // namespace game
} // namespace Amulet
