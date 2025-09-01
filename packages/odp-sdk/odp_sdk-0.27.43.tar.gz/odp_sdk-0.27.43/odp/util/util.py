import re
from math import log2

IEC_UNITS = ["KiB", "MiB", "GiB", "TiB"]


def size2human(size: int) -> str:
    if size == 0:
        return "0B"
    p = int(log2(size) // 10.0)

    if p < 1:
        return f"{size}B"
    if p > len(IEC_UNITS):
        p = len(IEC_UNITS)
    converted_size = size / 1024**p
    return f"{converted_size:.1f}{IEC_UNITS[p - 1]}"


_VALID = re.compile(r"^[a-zA-Z0-9_.-]+$")


def safe_id(s: str, empty: bool = False, max_len: int = 100) -> str:
    """
    check if the id is safe, raise an exception if not
    """
    if s is None:
        s = ""
    s = str(s)
    if s == "" and not empty:
        raise ValueError("id is empty")
    if not s:
        return ""
    if len(s) > max_len:
        raise ValueError(f"id is too long: {len(s)} > {max_len}")
    if not _VALID.match(s):
        raise ValueError(f"id contains invalid characters: {repr(s)}")
    return s
