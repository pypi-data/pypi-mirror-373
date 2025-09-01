from __future__ import annotations

from typing import List, Optional


def string_clean(val: Optional[str]) -> Optional[str]:
    """
    Trim string; treat empty, 'none' and 'null' as None.
    """
    if val is None:
        return None
    v = val.strip()
    if v == "" or v.lower() in {"none", "null"}:
        return None
    return v


# def string_clean(val: Optional[str]) -> Optional[str]:
#     return (val or "").strip() or None
