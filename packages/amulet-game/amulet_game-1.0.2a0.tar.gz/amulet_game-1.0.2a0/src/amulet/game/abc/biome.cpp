#include <pybind11/pybind11.h>

#include "biome.hpp"

#include <amulet/game/pyobj/wrapper.hpp>

namespace Amulet {
namespace game {

    Biome BiomeData::translate(const std::string& platform, const VersionNumber& version, const Biome& biome)
    {
        py::gil_scoped_acquire gil;
        return _obj.attr("translate")(platform, py::cast(version), py::cast(biome)).cast<Biome>();
    }

} // namespace game
} // namespace Amulet
