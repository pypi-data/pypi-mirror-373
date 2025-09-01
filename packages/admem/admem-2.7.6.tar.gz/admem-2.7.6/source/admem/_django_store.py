# Copyright (c) 2022-2025 Mario S. Könz; License: MIT
import collections
import dataclasses as dc
import enum
import types
import typing as tp
from pathlib import Path

from django.core.files import File
from django.core.files.storage import storages
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.db.models.fields.files import FieldFile

from ._create_django_model import InspectDataclass
from ._decorator import BACKEND_LINKER
from ._decorator import django_model
from ._path_proxy import DjangoPath
from ._protocols import T
from ._util import streaming_file_cmp


@dc.dataclass
class DjangoStore:
    identifier: str

    def dump(  # pylint: disable=too-many-locals
        self, dc_obj: tp.Any
    ) -> "tuple[models.Model, bool]":
        kwgs, m2m, update_origin = self.dataclass_to_django_kwgs(dc_obj)
        identifying, defaults = self._split_off_pk(dc_obj, kwgs)
        if identifying:
            dj_obj, created = self.backend_manager(dc_obj).update_or_create(
                **identifying, defaults=defaults
            )
        else:
            dj_obj = self.backend_manager(dc_obj).create(**defaults)
            created = True

        for key, fct in update_origin.items():
            try:
                setattr(dc_obj, key, fct(getattr(dj_obj, key)))
            except dc.FrozenInstanceError as err:
                raise RuntimeError(
                    f"cannot change attribute {key} due to dataclass being frozen, remove field or unfreeze!"
                ) from err

        weak_ref = self._get_weak_ref(dc_obj)
        for key, vals in m2m.items():
            # remove old ones
            if not created:
                getattr(dj_obj, key).clear()
            for val in vals:
                sub_dj_obj = self._load_or_dump(val, key in weak_ref)
                getattr(dj_obj, key).add(sub_dj_obj)

        return dj_obj, created

    def django_load(self, val: tp.Any) -> models.Model:
        param, *_ = self.dataclass_to_django_kwgs(val, pk_only=True)
        candidates = list(self.django_load_all(type(val), **param))
        if len(candidates) == 0:
            raise TypeError(
                f"are you sure that {val} has been dumped? Weak refs only work on data in the database."
            )
        if len(candidates) > 1:
            raise RuntimeError(
                "there should not be more than one candidate for weak refs."
            )

        return candidates[0]

    def load_all(self, dataclass: type[T], **filter_kwgs: tp.Any) -> tp.Iterator[T]:
        for instance in self.django_load_all(dataclass, **filter_kwgs):
            yield self.django_to_dataclass(instance)

    def django_load_all(
        self, dataclass: type[T], **filter_kwgs: tp.Any
    ) -> tp.Iterator[models.Model]:
        manager = self.backend_manager(dataclass)
        yield from manager.filter(**filter_kwgs).all()

    def dataclass_to_django_kwgs(self, dc_obj: tp.Any, pk_only: bool = False) -> tp.Any:
        model = django_model(dc_obj)
        kwgs = {}
        m2m = {}

        to_process = {field.name for field in dc.fields(dc_obj)}
        # sometimes we only want the fields necessary for
        # identifying the object of interest
        if pk_only:
            to_process = InspectDataclass(dc_obj).get_identifying_parameter()
        update_origin: dict[str, tp.Any] = {}
        weak_ref = self._get_weak_ref(dc_obj)
        for field in dc.fields(dc_obj):
            key = field.name
            if key not in to_process:
                continue

            val = getattr(dc_obj, key)
            if type(val) in BACKEND_LINKER.dc_to_backend:
                val = self._load_or_dump(val, key in weak_ref)
            if isinstance(val, enum.Enum):
                val = val.value
            if isinstance(val, Path):
                assert val is not None
                val = self._process_path(val, field, model, update_origin)

            # pylint: disable=protected-access
            dj_model = model._meta.get_field(key)
            if isinstance(dj_model, models.ManyToManyField):
                m2m[key] = val
            else:
                kwgs[key] = val

        return kwgs, m2m, update_origin

    def _process_path(  # pylint: disable=too-many-return-statements,too-many-branches,too-many-locals
        self,
        val: tp.Any,
        field: dc.Field[Path],
        model: type[models.Model],
        update_origin: dict[str, tp.Any],
    ) -> tp.Any:
        key = field.name
        storage = storages["default"]
        resave = field.metadata.get("resave", "always")
        # pylint: disable=protected-access
        dj_field = model._meta.get_field(key)
        create_dj_path = self.create_dj_path(model, field)

        def are_files_identical(prefix_name: str) -> bool:
            incomming = val.open("rb")
            existing = storage.open(prefix_name, "rb")
            return streaming_file_cmp(incomming, existing)  # type: ignore

        if isinstance(val, DjangoPath):
            # the DjangoPath can be from another Model,
            # hence we strip the prefix and add it again
            name = val.name_wo_prefix()
            prefix_name = dj_field.generate_filename(None, name)  # type: ignore
            cross_model = prefix_name != val.as_posix()

            def uploaded_file() -> UploadedFile:
                update_origin[key] = create_dj_path
                return UploadedFile(self._get_content(field, val), name)

            if resave == "always":
                return uploaded_file()
            if resave in ["first", "on_change"]:
                if not storage.exists(prefix_name):
                    if cross_model:
                        return uploaded_file()
                    raise FileNotFoundError(storage.path(prefix_name))

                if resave == "on_change":
                    # Note: we are not doing this, bc if its the same model, its already stored
                    #       and it should not be different, since it came from the StorageBackend.
                    #       In short: DjangoPaths come from the Backend, and dont hold new versions.
                    # if not are_files_identical(prefix_name):
                    #     return uploaded_file()
                    pass

                if cross_model:
                    return prefix_name
                val._committed = True  # type: ignore
                return val

            raise NotImplementedError(resave)
        if val.exists():
            prefix_name = dj_field.generate_filename(None, val.name)  # type: ignore
            update_origin[key] = create_dj_path
            exists = storage.exists(prefix_name)

            if resave == "first" and exists:
                return prefix_name
            if resave == "on_change" and exists:
                if are_files_identical(prefix_name):
                    return prefix_name

            if resave in ["always", "first", "on_change"]:
                name = val.name
                if resave == "on_change" and exists:
                    # this is a very specific need bc of how django
                    # handles the presents or absence of upload_to
                    # on overwrites.
                    name = storage.get_available_name(name)
                return File(
                    self._get_content(field, val),
                    name,
                )
            raise NotImplementedError(resave)
        raise FileNotFoundError(val)

    def _get_content(self, field: dc.Field[Path], val: Path) -> tp.Any:
        if val.is_dir():
            if field.metadata.get("allow_dir", False):
                return val
            raise IsADirectoryError(
                f"{val}, use 'path: Path = dc.field(metadata=dict(allow_dir=True)) in your dataclass to enable support"
            )
        return val.open("rb")

    def create_dj_path(
        self, model: type[models.Model], dc_field: dc.Field[Path]
    ) -> tp.Callable[[FieldFile], DjangoPath]:
        # pylint: disable=protected-access
        dj_field = model._meta.get_field(dc_field.name)
        prefix: str | None = None
        if hasattr(dj_field, "upload_to"):
            prefix = getattr(dj_field, "upload_to")

        def inner(fieldfile: FieldFile) -> DjangoPath:
            assert fieldfile.name
            res = DjangoPath(fieldfile.name, prefix=prefix)
            return res

        return inner

    @classmethod
    def _true_key_and_subkey(
        cls, keylist: tp.Iterable[str], is_only: bool = False
    ) -> tuple[set[str], dict[str, set[str]]]:
        subkeys = collections.defaultdict(set)
        truekeys = set()
        for key in keylist:
            if "__" in key:
                tkey, skey = key.split("__", 1)
                if is_only:
                    truekeys.add(tkey)
                subkeys[tkey].add(skey)
            else:
                truekeys.add(key)
        return truekeys, subkeys

    def django_to_dataclass(  # pylint: disable=too-many-locals
        self,
        dj_obj: models.Model,
        defer: tp.Iterable[str] = tuple(),
        only: tp.Iterable[str] = tuple(),
    ) -> tp.Any:
        dataclass = BACKEND_LINKER.backend_to_dc[type(dj_obj)]
        obj_kwgs: dict[str, tp.Any] = {}
        true_defer, sub_defer = self._true_key_and_subkey(defer)
        true_only, sub_only = self._true_key_and_subkey(only, is_only=True)
        for field in dc.fields(dataclass):
            key = field.name
            if key in true_defer or (true_only and key not in true_only):
                obj_kwgs[field.name] = None
                continue
            val = getattr(dj_obj, key)
            if type(val) in BACKEND_LINKER.backend_to_dc:
                val = self.django_to_dataclass(
                    val,
                    defer=sub_defer.get(field.name, set()),
                    only=sub_only.get(field.name, set()),
                )

            field_type = field.type
            origin = tp.get_origin(field_type)
            if origin:
                # pylint: disable=protected-access
                dj_field = dj_obj._meta.get_field(key)
                if origin == types.UnionType:
                    field_type, none_type = tp.get_args(field_type)
                    if none_type != type(None):
                        raise NotImplementedError(
                            "Union not supported yet, except for Optional"
                        )
                    if not val and isinstance(dj_field, models.FileField):
                        val = None

                    if val is None:
                        field_type = type(None)

                elif origin == set:
                    assert isinstance(dj_field, models.ManyToManyField)
                    defer = sub_defer.get(field.name, set())
                    only = sub_only.get(field.name, set())
                    query = val.defer(*defer).only(*only)
                    val = {self.django_to_dataclass(x, defer, only) for x in query}
                else:
                    raise RuntimeError(f"field type {origin} not supported yet!")

            if issubclass(field_type, enum.Enum):
                val = field_type(val)
            if issubclass(field_type, Path):
                create_dj_path = self.create_dj_path(dj_obj.__class__, field)
                val = create_dj_path(val)  # contains prefix
            obj_kwgs[field.name] = val
        return dataclass(**obj_kwgs)

    parse = django_to_dataclass

    def backend_manager(self, dataclass: type[T]) -> tp.Any:
        return django_model(dataclass).objects.using(self.identifier)

    @classmethod
    def _split_off_pk(
        cls, dc_obj: tp.Any, kwgs: dict[str, tp.Any]
    ) -> tuple[dict[str, tp.Any], dict[str, tp.Any]]:
        ident_keys = InspectDataclass(dc_obj).get_identifying_parameter()
        return (
            {key: kwgs[key] for key in kwgs.keys() & ident_keys},
            {key: kwgs[key] for key in kwgs.keys() ^ ident_keys if key in kwgs},
        )

    def reverse_set(self, dc_obj: tp.Any, relation: str) -> set[tp.Any] | tp.Any:
        model = self.backend_manager(dc_obj.__class__)
        identifying, *_ = self.dataclass_to_django_kwgs(dc_obj, pk_only=True)
        dj_obj = model.filter(**identifying).first()
        if dj_obj is None:
            raise TypeError(
                f"are you sure that {dc_obj} has been dumped? Reverse relations only work on data in the database."
            )
        precursor = getattr(dj_obj, relation)
        if isinstance(precursor, models.Manager):
            rev_dj_obj = precursor.all()
            return set(map(self.parse, rev_dj_obj))
        return self.parse(precursor)

    @classmethod
    def _get_weak_ref(cls, dc_obj: tp.Any) -> list[str]:
        weak_ref = []
        try:
            weak_ref = dc_obj.__class__.Meta.weak_ref
            assert isinstance(weak_ref, list)
        except AttributeError:
            pass
        return weak_ref

    def _load_or_dump(self, val: tp.Any, load: bool) -> models.Model:
        if load:
            return self.django_load(val)

        return self.dump(val)[0]
