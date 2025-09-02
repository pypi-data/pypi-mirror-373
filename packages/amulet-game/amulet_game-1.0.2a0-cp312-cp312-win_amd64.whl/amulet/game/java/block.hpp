#pragma once

#include <amulet/game/abc/block.hpp>

#include <amulet/game/dll.hpp>

namespace Amulet {
namespace game {

    enum class Waterloggable {
        No, // Cannot be waterlogged.
        Yes, // Can be waterlogged.
        Always // Is always waterlogged. (attribute is not stored)
    };

    class JavaBlockData : public BlockData {
    public:
        using BlockData::BlockData;
        using BlockData::operator=;

        AMULET_GAME_EXPORT Waterloggable is_waterloggable(const std::string& namespace_, const std::string& base_name);
    };

} // namespace game
} // namespace Amulet
