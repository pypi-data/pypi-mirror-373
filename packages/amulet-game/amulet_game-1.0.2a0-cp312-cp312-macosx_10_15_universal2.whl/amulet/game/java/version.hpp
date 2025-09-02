#pragma once

#include <amulet/game/abc/version.hpp>

#include "block.hpp"

#include <amulet/game/dll.hpp>

namespace Amulet {
namespace game {

    class JavaGameVersion : public GameVersion {
    public:
        using GameVersion::GameVersion;
        using GameVersion::operator=;

        AMULET_GAME_EXPORT std::shared_ptr<JavaBlockData> get_block_data();
    };

} // namespace game
} // namespace Amulet
