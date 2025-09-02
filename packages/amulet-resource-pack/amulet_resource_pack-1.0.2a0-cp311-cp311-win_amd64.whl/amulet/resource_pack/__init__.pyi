from __future__ import annotations

from amulet.resource_pack._load import load_resource_pack, load_resource_pack_manager
from amulet.resource_pack.abc.resource_pack import BaseResourcePack
from amulet.resource_pack.abc.resource_pack_manager import BaseResourcePackManager
from amulet.resource_pack.java.resource_pack import JavaResourcePack
from amulet.resource_pack.java.resource_pack_manager import JavaResourcePackManager
from amulet.resource_pack.unknown_resource_pack import UnknownResourcePack

from . import (
    _amulet_resource_pack,
    _load,
    _version,
    abc,
    image,
    java,
    mesh,
    unknown_resource_pack,
)

__all__ = [
    "BaseResourcePack",
    "BaseResourcePackManager",
    "JavaResourcePack",
    "JavaResourcePackManager",
    "UnknownResourcePack",
    "abc",
    "compiler_config",
    "image",
    "java",
    "load_resource_pack",
    "load_resource_pack_manager",
    "mesh",
    "unknown_resource_pack",
]

def _init() -> None: ...

__version__: str
compiler_config: dict
