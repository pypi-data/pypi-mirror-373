from __future__ import annotations

import PIL.Image

__all__: list[str] = ["get_missing_no_icon", "missing_no_icon_path"]

def get_missing_no_icon() -> PIL.Image.Image: ...

missing_no_icon_path: str
