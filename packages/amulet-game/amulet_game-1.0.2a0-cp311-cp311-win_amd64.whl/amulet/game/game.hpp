#pragma once

#include <memory>
#include <string>

#include <amulet/core/version/version.hpp>

#include <amulet/game/abc/version.hpp>
#include <amulet/game/java/version.hpp>

#include <amulet/game/dll.hpp>

namespace Amulet {
namespace game {

    AMULET_GAME_EXPORT std::shared_ptr<GameVersion> get_game_version(const std::string&, const VersionNumber& version);
    AMULET_GAME_EXPORT std::shared_ptr<JavaGameVersion> get_java_game_version(const VersionNumber& version);

} // namespace game
} // namespace Amulet
