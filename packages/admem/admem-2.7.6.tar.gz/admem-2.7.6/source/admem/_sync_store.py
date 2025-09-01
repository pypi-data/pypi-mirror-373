# Copyright (c) 2022-2025 Mario S. Könz; License: MIT
import contextlib
import typing as tp

from ._backend_manager_proxy import BackendManagerProxy
from ._protocols import BackendStoreProtocol
from ._protocols import T
from ._store_setup import ACTIVE_STORES

__all__ = ["store", "switch_store", "switched_store"]


class SyncStore:
    @classmethod
    def get_last_active(cls) -> BackendStoreProtocol:
        return next(reversed(ACTIVE_STORES.values()))

    @classmethod
    def get_last_active_key(cls) -> str:
        return next(reversed(ACTIVE_STORES))

    @property
    def impl(self) -> BackendStoreProtocol:
        return self.get_last_active()

    def dump(self, obj: tp.Any) -> bool:
        if hasattr(obj, "pre_save"):
            obj.pre_save()
        _, created = self.impl.dump(obj)
        if hasattr(obj, "post_save"):
            obj.post_save(created)
        return created  # type: ignore

    def load_all(self, dataclass: type[T], **filter_kwgs: tp.Any) -> tp.Iterator[T]:
        yield from self.impl.load_all(dataclass, **filter_kwgs)

    def load(self, dataclass: type[T], **filter_kwgs: tp.Any) -> T:
        hits = list(self.load_all(dataclass, **filter_kwgs))
        if len(hits) > 1:
            raise RuntimeError(
                f"found {len(hits)} entries matching filter_kwgs {filter_kwgs}, be more specific!"
            )
        if len(hits) == 0:
            raise RuntimeError(f"found no entries matching filter_kwgs {filter_kwgs}!")
        return hits[0]

    def __getitem__(self, dataclass: type[T]) -> BackendManagerProxy:
        return BackendManagerProxy(self.impl, self.impl.backend_manager(dataclass))

    def reverse_relation(self, relation: str) -> property:
        def inner(iself: tp.Any) -> set[tp.Any] | tp.Any:
            return self.impl.reverse_set(iself, relation)

        inner.__name__ = relation
        return property(inner)


store = SyncStore()


def switch_store(identifier: str) -> None:
    ACTIVE_STORES.move_to_end(identifier)


@contextlib.contextmanager
def switched_store(identifier: str) -> tp.Iterator[None]:
    last_key = store.get_last_active_key()
    switch_store(identifier)
    yield
    ACTIVE_STORES.move_to_end(last_key)
    switch_store(last_key)
