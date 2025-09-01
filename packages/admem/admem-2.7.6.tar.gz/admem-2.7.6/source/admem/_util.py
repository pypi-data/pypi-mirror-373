# Copyright (c) 2022-2025 Mario S. Könz; License: MIT
import typing as tp

__all__ = ["public_name"]


def public_name(cls: tp.Type[tp.Any], without_cls: bool = False) -> str:
    parts = []
    for part in cls.__module__.split("."):
        if part.startswith("_"):
            continue
        parts.append(part)

    public_module = "main"
    if parts:
        public_module = ".".join(parts)

    if without_cls:
        return f"{public_module}"
    return f"{public_module}.{cls.__name__}"


def streaming_file_cmp(
    f1: tp.BinaryIO, f2: tp.BinaryIO, chunk_size: int = 1024 * 1024
) -> bool:
    """Return True if two binary file-like objects have identical bytes."""
    while True:
        b1 = f1.read(chunk_size)
        b2 = f2.read(chunk_size)
        if b1 != b2:
            return False
        if not b1:
            return True
