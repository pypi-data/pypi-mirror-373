#include "version.hpp"

namespace Amulet {
namespace game {

    std::shared_ptr<JavaBlockData> JavaGameVersion::get_block_data()
    {
        py::gil_scoped_acquire gil;
        return std::make_shared<JavaBlockData>(_obj.attr("block"));
    }

} // namespace game
} // namespace Amulet
