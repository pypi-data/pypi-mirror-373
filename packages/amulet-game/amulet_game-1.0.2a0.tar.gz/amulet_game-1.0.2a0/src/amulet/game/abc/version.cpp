#include "version.hpp"

#include <amulet/game/pyobj/wrapper.hpp>

namespace Amulet {
namespace game {

    std::shared_ptr<BiomeData> GameVersion::get_biome_data()
    {
        py::gil_scoped_acquire gil;
        return std::make_shared<BiomeData>(_obj.attr("biome"));
    }

    std::shared_ptr<BlockData> GameVersion::get_block_data()
    {
        py::gil_scoped_acquire gil;
        return std::make_shared<BlockData>(_obj.attr("block"));
    }

} // namespace game
} // namespace Amulet
