import os
import subprocess
import sys
from pathlib import Path
import platform
import glob
import json
import gzip
import pickle
from tempfile import TemporaryDirectory

from setuptools import setup, Extension, Command
from setuptools.command.build import build
from setuptools.command.build_ext import build_ext

import versioneer

import requirements


def fix_path(path: str) -> str:
    return os.path.realpath(path).replace(os.sep, "/")


cmdclass: dict[str, type[Command]] = versioneer.get_cmdclass()


class CMakeBuild(cmdclass.get("build_ext", build_ext)):
    def build_extension(self, ext):
        import pybind11
        import amulet.pybind11_extensions
        import amulet.io
        import amulet.utils
        import amulet.nbt
        import amulet.core

        ext_dir = (
            (Path.cwd() / self.get_ext_fullpath("")).parent.resolve()
            / "amulet"
            / "game"
        )
        game_src_dir = (
            Path.cwd() / "src" / "amulet" / "game" if self.editable_mode else ext_dir
        )

        platform_args = []
        if sys.platform == "win32":
            platform_args.extend(["-G", "Visual Studio 17 2022"])
            if sys.maxsize > 2**32:
                platform_args.extend(["-A", "x64"])
            else:
                platform_args.extend(["-A", "Win32"])
            platform_args.extend(["-T", "v143"])
        elif sys.platform == "darwin":
            if platform.machine() == "arm64":
                platform_args.append("-DCMAKE_OSX_ARCHITECTURES=x86_64;arm64")

        if subprocess.run(["cmake", "--version"]).returncode:
            raise RuntimeError("Could not find cmake")
        with TemporaryDirectory() as tempdir:
            if subprocess.run(
                [
                    "cmake",
                    *platform_args,
                    f"-DPYTHON_EXECUTABLE={sys.executable}",
                    f"-Dpybind11_DIR={fix_path(pybind11.get_cmake_dir())}",
                    f"-Damulet_pybind11_extensions_DIR={fix_path(amulet.pybind11_extensions.__path__[0])}",
                    f"-Damulet_io_DIR={fix_path(amulet.io.__path__[0])}",
                    f"-Damulet_utils_DIR={fix_path(amulet.utils.__path__[0])}",
                    f"-Damulet_nbt_DIR={fix_path(amulet.nbt.__path__[0])}",
                    f"-Damulet_core_DIR={fix_path(amulet.core.__path__[0])}",
                    f"-Damulet_game_DIR={fix_path(game_src_dir)}",
                    f"-DAMULET_GAME_EXT_DIR={fix_path(ext_dir)}",
                    f"-DCMAKE_INSTALL_PREFIX=install",
                    "-B",
                    tempdir,
                ]
            ).returncode:
                raise RuntimeError("Error configuring amulet-game")
            if subprocess.run(
                ["cmake", "--build", tempdir, "--config", "Release"]
            ).returncode:
                raise RuntimeError("Error building amulet-game")
            if subprocess.run(
                ["cmake", "--install", tempdir, "--config", "Release"]
            ).returncode:
                raise RuntimeError("Error installing amulet-game")


class MinifyJSON(Command):
    def initialize_options(self):
        self.editable_mode = False
        self.build_lib = None

    def finalize_options(self):
        self.set_undefined_options("build_py", ("build_lib", "build_lib"))

    def run(self):
        # This is rather janky but it is a stop-gap until the whole library can be ported to C++
        if self.editable_mode:
            src_dir = os.path.abspath("src")
        else:
            src_dir = self.build_lib

        sys.path.append(src_dir)

        from amulet.game.abc import GameVersion
        from amulet.game.java import JavaGameVersion
        from amulet.game.bedrock import BedrockGameVersion
        from amulet.game.universal import UniversalVersion

        json_path = os.path.join("submodules", "PyMCTranslate", "PyMCTranslate", "json")

        universal_version = UniversalVersion.from_json(
            os.path.join(json_path, "versions", "universal")
        )
        _versions: dict[str, list[GameVersion]] = {
            "universal": [universal_version],
        }
        for init_path in glob.glob(
            os.path.join(glob.escape(json_path), "versions", "*", "__init__.json")
        ):
            version_path = os.path.dirname(init_path)

            with open(os.path.join(version_path, "__init__.json")) as f:
                init = json.load(f)

            platform = init["platform"]
            if platform == "bedrock":
                _versions.setdefault("bedrock", []).append(
                    BedrockGameVersion.from_json(version_path, universal_version)
                )
            elif platform == "java":
                _versions.setdefault("java", []).append(
                    JavaGameVersion.from_json(version_path, universal_version)
                )
            elif platform == "universal":
                pass
            else:
                raise RuntimeError
        with open(
            os.path.join(src_dir, "amulet", "game", "versions.pkl.gz"), "wb"
        ) as pkl:
            pkl.write(gzip.compress(pickle.dumps(_versions)))


# register a new command class
cmdclass["minify_json"] = MinifyJSON
# register our command class as a subcommand of the build command class
cmdclass.get("build", build).sub_commands.append(("minify_json", None))


cmdclass["build_ext"] = CMakeBuild


setup(
    version=versioneer.get_version(),
    cmdclass=cmdclass,
    ext_modules=[Extension("amulet.game._amulet_game", [])]
    * (not os.environ.get("AMULET_SKIP_COMPILE", None)),
    install_requires=requirements.get_runtime_dependencies(),
)
