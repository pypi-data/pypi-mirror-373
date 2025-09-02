#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "block.hpp"
#include <amulet/game/pyobj/wrapper.hpp>

namespace Amulet {
namespace game {

    std::variant<
        std::tuple<Block, std::optional<BlockEntity>, bool>,
        std::tuple<Entity, bool>>
    BlockData::translate(const std::string& platform, const VersionNumber& version, const Block& block)
    {
        py::gil_scoped_acquire gil;
        py::tuple out = _obj.attr("translate")("java", version, block);
        if (py::isinstance<Block>(out[0])) {
            return out.cast<std::tuple<Block, std::optional<BlockEntity>, bool>>();
        } else {
            return std::make_tuple(out[0].cast<Entity>(), out[2].cast<bool>());
        }
    }

} // namespace game
} // namespace Amulet
