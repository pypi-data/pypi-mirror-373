from __future__ import annotations

import PIL.Image

__all__ = ["get_missing_pack_icon", "missing_pack_icon_path"]

def get_missing_pack_icon() -> PIL.Image.Image: ...

missing_pack_icon_path: str
