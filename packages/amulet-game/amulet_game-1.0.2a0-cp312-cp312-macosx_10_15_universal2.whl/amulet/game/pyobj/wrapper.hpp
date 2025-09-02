#pragma once

#include <pybind11/pybind11.h>

#include <amulet/game/dll.hpp>

namespace py = pybind11;

namespace Amulet {
namespace game {

    class PyObjWrapper {
    protected:
        py::object _obj;

    public:
        AMULET_GAME_EXPORT PyObjWrapper(const py::object& obj);

        AMULET_GAME_EXPORT PyObjWrapper(py::object&& obj);

        AMULET_GAME_EXPORT PyObjWrapper(const PyObjWrapper& other);

        AMULET_GAME_EXPORT PyObjWrapper(PyObjWrapper&& other) noexcept;

        AMULET_GAME_EXPORT PyObjWrapper& operator=(const PyObjWrapper& other);

        AMULET_GAME_EXPORT PyObjWrapper& operator=(PyObjWrapper&& other) noexcept;

        AMULET_GAME_EXPORT ~PyObjWrapper();
    };

} // namespace game
} // namespace Amulet
