#include "block.hpp"

namespace Amulet {
namespace game {

    Waterloggable JavaBlockData::is_waterloggable(const std::string& namespace_, const std::string& base_name)
    {
        py::gil_scoped_acquire gil;
        return _obj.attr("waterloggable")(namespace_, base_name).cast<Waterloggable>();
    }

} // namespace game
} // namespace Amulet
