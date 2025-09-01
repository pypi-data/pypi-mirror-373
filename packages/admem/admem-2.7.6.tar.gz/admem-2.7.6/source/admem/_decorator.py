# Copyright (c) 2022-2025 Mario S. Könz; License: MIT
import dataclasses as dc
import typing as tp

from django.db import models

__all__ = ["BACKEND_LINKER", "register_app_label", "django_model"]


@dc.dataclass
class BackendLinker:
    dc_to_backend: dict[type, type] = dc.field(default_factory=dict)
    backend_to_dc: dict[type, type] = dc.field(default_factory=dict)
    app_labels: set[str] = dc.field(default_factory=set)

    def link(self, dataclass: type, backendclass: type) -> None:
        self.dc_to_backend[dataclass] = backendclass
        self.backend_to_dc[backendclass] = dataclass

    def backend_class(self, dc_obj_or_dataclass: type | tp.Any) -> type:
        if isinstance(dc_obj_or_dataclass, type):
            dataclass = dc_obj_or_dataclass
        else:
            dataclass = type(dc_obj_or_dataclass)
        try:
            return self.dc_to_backend[dataclass]
        except KeyError as err:
            raise KeyError(
                f"{dataclass} not found, have you forgotten to admem.create_django_model or similar?"
            ) from err

    def django_backend_classes(self) -> tp.Iterator[type[models.Model]]:
        for key in self.backend_to_dc:
            if issubclass(key, models.Model):
                yield key


BACKEND_LINKER = BackendLinker()


def register_app_label(app_label: str) -> None:
    BACKEND_LINKER.app_labels.add(app_label)


def django_model(dataclass: type) -> "type[models.Model]":
    backend = BACKEND_LINKER.backend_class(dataclass)
    assert issubclass(backend, models.Model)
    return backend
