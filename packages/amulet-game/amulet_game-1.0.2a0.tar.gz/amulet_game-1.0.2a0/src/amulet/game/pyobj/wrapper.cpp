#include <amulet/game/pyobj/wrapper.hpp>

namespace Amulet {
namespace game {

    PyObjWrapper::PyObjWrapper(const py::object& obj)
    {
        py::gil_scoped_acquire gil;
        _obj = obj;
    }

    PyObjWrapper::PyObjWrapper(py::object&& obj)
        : _obj(std::move(obj))
    {
    }

    PyObjWrapper::PyObjWrapper(const PyObjWrapper& other)
    {
        py::gil_scoped_acquire gil;
        _obj = other._obj;
    }

    PyObjWrapper::PyObjWrapper(PyObjWrapper&& other) noexcept
        : _obj(std::move(other._obj))
    {
    }

    PyObjWrapper& PyObjWrapper::operator=(const PyObjWrapper& other)
    {
        py::gil_scoped_acquire gil;
        _obj = other._obj;
        return *this;
    }

    PyObjWrapper& PyObjWrapper::operator=(PyObjWrapper&& other) noexcept
    {
        py::gil_scoped_acquire gil;
        _obj = std::move(other._obj);
        return *this;
    }

    PyObjWrapper::~PyObjWrapper()
    {
        py::gil_scoped_acquire gil;
        _obj.release().dec_ref();
    }

} // namespace game
} // namespace Amulet
