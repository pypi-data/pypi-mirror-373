# Copyright (c) 2022-2025 Mario S. Könz; License: MIT
import dataclasses as dc
import typing as tp
from collections.abc import Iterable

from ._protocols import BackendStoreProtocol

__all__ = ["BackendManagerProxy"]


@dc.dataclass
class BackendManagerProxy:
    backend: BackendStoreProtocol
    internal: tp.Any
    calls: list[str] = dc.field(default_factory=list)

    _collect_only: tuple[str, ...] = tuple()
    _collect_defer: tuple[str, ...] = tuple()

    def __getattr__(self, key: str) -> "BackendManagerProxy":
        self.calls.append(key)
        return self

    def __call__(self, *args: tp.Any, **kwgs: tp.Any) -> "BackendManagerProxy":
        assert self.calls
        if self.calls[-1] == "only":
            self._collect_defer = tuple()
            self._collect_only = args
        elif self.calls[-1] == "defer":
            if len(args) == 1 and args[0] is None:
                self._collect_defer = tuple()
            else:
                self._collect_defer += args
        self.internal = getattr(self.internal, self.calls[-1])(*args, **kwgs)
        return self

    def dci(self) -> tp.Iterator[tp.Any]:  # dataclass iterator
        if isinstance(self.internal, Iterable):
            for obj in self.internal:
                yield self.backend.parse(
                    obj, defer=self._collect_defer, only=self._collect_only
                )
        else:
            yield self.backend.parse(
                self.internal, defer=self._collect_defer, only=self._collect_only
            )

    def dcl(self) -> tp.Any | list[tp.Any]:  # dataclass list
        res = list(self.dci())
        if not isinstance(self.internal, Iterable):
            return res[0]
        return res

    def nat(self) -> tp.Any:  # native
        return self.internal
