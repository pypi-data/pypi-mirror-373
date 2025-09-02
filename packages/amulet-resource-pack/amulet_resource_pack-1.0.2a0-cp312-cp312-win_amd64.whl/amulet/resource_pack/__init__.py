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
        lib_path = os.path.join(os.path.dirname(__file__), "amulet_resource_pack.dll")
    elif sys.platform == "darwin":
        lib_path = os.path.join(
            os.path.dirname(__file__), "libamulet_resource_pack.dylib"
        )
    elif sys.platform == "linux":
        lib_path = os.path.join(os.path.dirname(__file__), "libamulet_resource_pack.so")
    else:
        raise RuntimeError(f"Unsupported platform {sys.platform}")

    # Import dependencies
    import amulet.utils
    import amulet.zlib
    import amulet.nbt
    import amulet.core

    # Load the shared library
    ctypes.cdll.LoadLibrary(lib_path)

    from ._amulet_resource_pack import init

    init(sys.modules[__name__])


_init()

from amulet.resource_pack.abc import (
    BaseResourcePack,
    BaseResourcePackManager,
)

from .unknown_resource_pack import UnknownResourcePack

from amulet.resource_pack.java import (
    JavaResourcePack,
    JavaResourcePackManager,
)

# from amulet.resource_pack.bedrock import (
#     BedrockResourcePack,
#     BedrockResourcePackManager,
# )

from ._load import load_resource_pack, load_resource_pack_manager
