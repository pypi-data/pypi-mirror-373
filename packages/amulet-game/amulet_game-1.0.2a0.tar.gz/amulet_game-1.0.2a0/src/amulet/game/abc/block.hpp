#pragma once

#include <memory>
#include <optional>
#include <variant>

#include <amulet/core/block/block.hpp>
#include <amulet/core/block_entity/block_entity.hpp>
#include <amulet/core/entity/entity.hpp>

#include <amulet/game/dll.hpp>

#include <amulet/game/pyobj/wrapper.hpp>

namespace py = pybind11;

namespace Amulet {
namespace game {

    class BlockData : public PyObjWrapper {
    public:
        using PyObjWrapper::PyObjWrapper;
        using PyObjWrapper::operator=;

        AMULET_GAME_EXPORT std::variant<
            std::tuple<Block, std::optional<BlockEntity>, bool>,
            std::tuple<Entity, bool>>
        translate(const std::string& platform, const VersionNumber& version, const Block& block);
    };

} // namespace game
} // namespace Amulet
