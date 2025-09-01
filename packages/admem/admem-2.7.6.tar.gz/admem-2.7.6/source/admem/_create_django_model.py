# Copyright (c) 2022-2025 Mario S. Könz; License: MIT
import dataclasses as dc
import datetime
import enum
import types
import typing
import typing as tp  # pylint: disable=reimported
from pathlib import Path

import django.db  # pylint: disable=unused-import
from django.db import models

from ._decorator import BACKEND_LINKER
from ._decorator import django_model
from ._inspect_dataclass import InspectDataclass
from ._util import public_name

# 2023-Q1: sphinx has a bug regarding adjusting the signature for attributes,
# hence I need fully qualified imports for typing and django.db

__all__ = ["CreateDjangoModel", "create_django_model"]


@dc.dataclass(frozen=True)
class CreateDjangoModel(InspectDataclass):
    alt_field_type: (
        "dict[str, type[django.db.models.Field[typing.Any, typing.Any]]]"
    ) = dc.field(default_factory=dict)

    def __post_init__(self) -> None:
        # evaluate the Meta class
        (
            pk_key,
            unique_together,
            extra_kwgs,
            ordering,
            app_label,
            db_table,
        ) = self.extract_meta()

        if not (unique_together or pk_key):
            raise RuntimeError("specify either unique_together or pk_key")
        # translate fields
        fields: dict[str, tp.Any] = self.translate_fields(pk_key, extra_kwgs)
        fields["Meta"] = self.generate_meta(
            unique_together, ordering, app_label, db_table
        )
        # pylint: disable=comparison-with-callable
        if self.dataclass.__str__ != object.__str__:  # type: ignore
            fields["__str__"] = self.dataclass.__str__
        fields["__module__"] = fields["Meta"].app_label
        if "." in fields["Meta"].app_label:
            fields["Meta"].app_label = fields["Meta"].app_label.rsplit(".", 1)[1]
        dj_model = type(self.dataclass.__name__, (models.Model,), fields)
        BACKEND_LINKER.link(self.dataclass, dj_model)

    def translate_fields(
        self, pk_key: str | None, extra_kwgs: dict[str, dict[str, tp.Any]] | None
    ) -> "dict[str, models.Field[tp.Any, tp.Any]]":
        fields = {}
        fields_to_skip = {Path: ["resave", "allow_dir"], Path | None: ["resave"]}
        for field in dc.fields(self.dataclass):
            try:
                django_field = self.alt_field_type.pop(field.name)
                opts: dict[str, tp.Any] = {}
            except KeyError:
                django_field, opts = self.django_field_precursor(field.type)
            if field.name == pk_key:
                opts["primary_key"] = True
                if django_field is models.ForeignKey:
                    django_field = models.OneToOneField
            default = self.get_default(field)
            if default is not dc.MISSING:
                opts["default"] = default
            extra = dict(**field.metadata)
            if extra_kwgs:
                extra.update(extra_kwgs.pop(field.name, {}))
            for key in fields_to_skip.get(field.type, []):
                extra.pop(key, None)
            fields[field.name] = django_field(**{**opts, **extra})
        if extra_kwgs:
            raise RuntimeError(
                f"unconsumed extra kwgs ({extra_kwgs}) found for {self.dataclass}, please adjust!"
            )
        if self.alt_field_type:
            raise RuntimeError(
                f"unused alt_field_type ({self.alt_field_type}) found for {self.dataclass}, please adjust!"
            )

        return fields

    def generate_meta(
        self,
        unique_together: list[str] | None,
        ordering: list[str] | None,
        app_label: str | None,
        db_table: str | None,
    ) -> type:
        if app_label is None:
            app_label = public_name(self.dataclass, without_cls=True)
        if db_table is None:
            db_table = public_name(self.dataclass)

        class Meta:
            pass

        Meta.app_label = app_label  # type: ignore
        Meta.db_table = db_table  # type: ignore

        if unique_together:
            Meta.unique_together = unique_together  # type: ignore

        if ordering:
            Meta.ordering = ordering  # type: ignore
        return Meta

    @classmethod
    def django_field_precursor(
        cls, type_: type
    ) -> "tuple[type[models.Field[tp.Any, tp.Any]], dict[str, tp.Any]]":
        # pylint: disable=too-many-return-statements,too-many-branches
        if type_ == str:
            return models.CharField, dict(max_length=1024)
        if type_ == int:
            return models.IntegerField, {}
        if type_ == float:
            return models.FloatField, {}
        if type_ == datetime.datetime:
            return models.DateTimeField, {}
        if type_ == datetime.date:
            return models.DateField, {}
        if type_ == datetime.time:
            return models.TimeField, {}
        if type_ == bytes:
            return models.BinaryField, dict(editable=True)
        if type_ == bool:
            return models.BooleanField, {}

        if isinstance(type_, types.GenericAlias):
            origin = tp.get_origin(type_)
            subtypes = tp.get_args(type_)
            if origin is set:
                assert len(subtypes) == 1
                subtype = subtypes[0]
                try:
                    fk_class = BACKEND_LINKER.backend_class(subtype)
                    assert issubclass(fk_class, models.Model)
                    return models.ManyToManyField, dict(to=fk_class, related_name="+")
                except KeyError:
                    pass

        if isinstance(type_, types.UnionType):
            target_type, none_type = tp.get_args(type_)
            if none_type is type(None):
                field, kwgs = cls.django_field_precursor(target_type)
                kwgs["blank"] = True
                kwgs["null"] = True
                return field, kwgs

        if issubclass(type_, enum.Enum):
            max_length = 256
            choices = []
            for val in type_.__members__.values():
                choices.append((val.value, val.value))
                assert len(val.value) < max_length

            return models.CharField, dict(max_length=max_length, choices=choices)

        if issubclass(type_, Path):
            return models.FileField, dict(max_length=1024)

        try:  # try Foreign Key relation (many-to-one)
            fk_class = BACKEND_LINKER.backend_class(type_)
            assert issubclass(fk_class, models.Model)
            return models.ForeignKey, dict(
                to=fk_class, on_delete=models.CASCADE, related_name="+"
            )

        except KeyError:
            pass

        raise NotImplementedError(type_)


def create_django_model(
    dataclass: type,
    alt_field_type: "dict[str, type[models.Field[tp.Any, tp.Any]]] | None" = None,
) -> "type[models.Model]":
    alt_field_type = alt_field_type or {}
    CreateDjangoModel(dataclass, alt_field_type)
    return django_model(dataclass)
