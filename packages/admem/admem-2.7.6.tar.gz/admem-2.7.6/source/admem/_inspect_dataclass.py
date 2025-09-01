# Copyright (c) 2022-2025 Mario S. Könz; License: MIT
import dataclasses as dc
import typing as tp

__all__ = ["InspectDataclass"]


@dc.dataclass(frozen=True)
class InspectDataclass:
    dataclass: type

    def extract_meta(
        self,
    ) -> tuple[
        str | None,
        list[str] | None,
        dict[str, dict[str, tp.Any]] | None,
        list[str] | None,
        str | None,
        str | None,
    ]:
        pk_key, unique_together, extra_kwgs, ordering, app_label, db_table = (
            None,
            None,
            None,
            None,
            None,
            None,
        )
        if hasattr(self.dataclass, "Meta"):
            meta = self.dataclass.Meta
            if hasattr(meta, "primary_key"):
                pk_key = meta.primary_key
                if not isinstance(pk_key, str):
                    raise RuntimeError("primary_key must be a string, please fix!")
            if hasattr(meta, "unique_together"):
                unique_together = meta.unique_together
                assert isinstance(unique_together, list)
            if hasattr(meta, "extra"):
                extra_kwgs = meta.extra
                assert isinstance(extra_kwgs, dict)
            if hasattr(meta, "ordering"):
                ordering = meta.ordering
                assert isinstance(ordering, list)
            if hasattr(meta, "app_label"):
                app_label = meta.app_label
                assert isinstance(app_label, str)
            if hasattr(meta, "db_table"):
                db_table = meta.db_table
                assert isinstance(db_table, str)

        return pk_key, unique_together, extra_kwgs, ordering, app_label, db_table

    def get_identifying_parameter(self) -> set[str]:
        pk_key, unique_together, *_ = self.extract_meta()
        res = set()
        if pk_key is not None:
            res.add(pk_key)
        if unique_together is not None:
            res.update(unique_together)
        return res

    @classmethod
    def get_default(cls, field: dc.Field[tp.Any]) -> tp.Any:
        if field.default != dc.MISSING:
            assert field.default_factory is dc.MISSING
            return field.default
        if field.default_factory != dc.MISSING:
            assert field.default is dc.MISSING
            return field.default_factory
        return dc.MISSING
