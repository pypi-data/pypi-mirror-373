"""
A module to store data about the game including state enumerations and translations between different game versions.
"""

import logging as _logging

from . import _version

__version__ = _version.get_versions()["version"]

# init a default logger
_logging.basicConfig(level=_logging.INFO, format="%(levelname)s - %(message)s")


def _init() -> None:
    import os
    import sys
    import ctypes

    if sys.platform == "win32":
        lib_path = os.path.join(os.path.dirname(__file__), "amulet_game.dll")
    elif sys.platform == "darwin":
        lib_path = os.path.join(os.path.dirname(__file__), "libamulet_game.dylib")
    elif sys.platform == "linux":
        lib_path = os.path.join(os.path.dirname(__file__), "libamulet_game.so")
    else:
        raise RuntimeError(f"Unsupported platform {sys.platform}")

    # Import dependencies
    import amulet.utils
    import amulet.zlib
    import amulet.nbt
    import amulet.core

    # Load the shared library
    ctypes.cdll.LoadLibrary(lib_path)

    from ._amulet_game import init

    init(sys.modules[__name__])


_init()

from .game import game_platforms, game_versions, get_game_version
from .java import JavaGameVersion
from .bedrock import BedrockGameVersion
