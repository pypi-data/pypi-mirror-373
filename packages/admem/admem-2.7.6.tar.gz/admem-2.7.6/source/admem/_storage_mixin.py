# Copyright (c) 2022-2025 Mario S. Könz; License: MIT
import typing as tp
from pathlib import Path

from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import UploadedFile

from ._path_proxy import DjangoPath


__all__ = ["DirectoryFSS", "DirectoryFSSMixin"]


class DirectoryFSSMixin:
    def _dir_save(self, dir_name: str, path: Path) -> str:
        for obj in path.iterdir():
            name = (dir_name / obj.relative_to(path)).as_posix()
            if isinstance(path, DjangoPath):
                FileType: tp.Any = UploadedFile
            else:
                FileType = File
            if obj.is_dir():
                content = FileType(obj)
            else:
                content = FileType(
                    obj.open("rb"),  # pylint: disable=consider-using-with
                    name,
                )
            self._save(name, content)
        return dir_name

    def _save(self, name: str, content: "File[tp.Any]") -> str:
        if isinstance(content.file, Path):
            path: Path = content.file
            assert path.is_dir()
            return self._dir_save(name, path)
        return super()._save(name, content)  # type: ignore


class DirectoryFSS(DirectoryFSSMixin, FileSystemStorage):
    pass
