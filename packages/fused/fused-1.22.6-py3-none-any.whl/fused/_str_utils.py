from __future__ import annotations

import uuid
from pathlib import Path
from typing import TypeVar
from urllib.parse import urlparse

T = TypeVar("T")


def is_url(path):
    prefixes = ["http://", "https://", "www."]
    return any(path.startswith(prefix) for prefix in prefixes)


def detect_passing_local_file_as_str(input: T) -> T | Path:
    if isinstance(input, str):
        try:
            parsed_url = urlparse(input)
            if parsed_url.scheme:
                # Do not do any rewriting if an explicit URL is passed in
                return input
        except:  # noqa: E722
            # Fall through to checking whether it exists as file
            pass

        as_path = Path(input)
        is_maybe_file = as_path.exists()

        if is_maybe_file:
            return as_path
    return input


def append_url_part(base: str, part: str) -> str:
    if base.endswith("/"):
        return f"{base[:-1]}/{part}"
    else:
        return f"{base}/{part}"


def is_uuid(s: str):
    try:
        uuid.UUID(s)
    except (ValueError, TypeError):
        return False
    return True
