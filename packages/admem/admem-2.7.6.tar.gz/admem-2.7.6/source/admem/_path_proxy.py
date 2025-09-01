# Copyright (c) 2022-2025 Mario S. Könz; License: MIT
import os
import typing as tp  # pylint: disable=reimported
from pathlib import _posix_flavour  # type: ignore
from pathlib import _windows_flavour  # type: ignore
from pathlib import Path
from pathlib import PosixPath
from pathlib import WindowsPath

from django.core.files.storage import storages

# 2023-Q1: sphinx has a bug regarding adjusting the signature for attributes,
# hence I need fully qualified imports for typing and django.db

__all__ = ["DjangoPath"]


class DjangoPath(Path):
    _flavour = _windows_flavour if os.name == "nt" else _posix_flavour
    __slots__ = ("_prefix",)

    def __new__(  # pylint: disable=arguments-differ
        cls, *args: str, prefix: str | None = None
    ) -> "DjangoPath":
        # pylint: disable=no-member,self-cls-assignment
        cls = DjangoPosixPath
        if os.name == "nt":
            cls = DjangoWindowsPath
        res = super().__new__(cls, *args)
        res._prefix = prefix  # type: ignore
        return res

    def name_wo_prefix(self) -> str:
        name = self.as_posix()
        # pylint: disable=no-member

        if self._prefix:  # type: ignore
            name = name.split(self._prefix + "/", 1)[1]  # type: ignore
        return name

    def __copy__(self) -> "DjangoPath":
        # pylint: disable=no-member
        return self.__class__(self, prefix=self._prefix)  # type: ignore

    def __deepcopy__(self, memo: dict[str, tp.Any]) -> "DjangoPath":
        # pylint: disable=no-member
        return self.__class__(self, prefix=self._prefix)  # type: ignore

    def open(  # type: ignore  # pylint: disable=too-many-arguments
        self,
        mode: str = "r",
        buffering: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> tp.IO[tp.Any]:
        # assert encoding is None
        assert errors is None
        assert newline is None
        assert buffering == -1
        media_storage = storages["default"]
        return media_storage.open(self.as_posix(), mode=mode)

    def iterdir(self) -> tp.Generator["DjangoPath", None, None]:
        media_storage = storages["default"]
        dirs, files = media_storage.listdir(self.as_posix())
        for path in dirs + files:
            yield self / path

    def is_dir(self) -> bool:
        try:
            with self.open():
                return False
        except IsADirectoryError:
            return True


class DjangoPosixPath(PosixPath, DjangoPath):  # pylint: disable=abstract-method
    pass


class DjangoWindowsPath(WindowsPath, DjangoPath):  # pylint: disable=abstract-method
    pass
