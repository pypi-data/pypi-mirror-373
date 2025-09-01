# Copyright (c) 2022-2025 Mario S. Könz; License: MIT
import collections
import contextlib
import io
import typing as tp
from pathlib import Path

import django
from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.core.signals import setting_changed
from django.db import connections

from ._decorator import BACKEND_LINKER
from ._django_store import DjangoStore
from ._protocols import BackendStoreProtocol

__all__ = ["set_store", "set_store_for_django", "ACTIVE_STORES", "set_file_backend"]

ACTIVE_STORES: collections.OrderedDict[str, BackendStoreProtocol] = (
    collections.OrderedDict()
)


def set_store(
    identifier: str = "first", flavor: str = "sqlite3", **kwgs: tp.Any
) -> None:
    if identifier in ACTIVE_STORES:
        raise RuntimeError(f"cannot set store {identifier}, because it is already set!")
    if flavor == "sqlite3":
        with django_setup(identifier) as databases:
            assert identifier not in databases
            databases[identifier] = dict(
                NAME=kwgs["path"],
                ENGINE="django.db.backends.sqlite3",
                TIME_ZONE="UTC",
                USE_TZ=True,
            )
            ACTIVE_STORES[identifier] = DjangoStore(identifier)
    elif flavor in ["postgres"]:
        with django_setup(identifier) as databases:
            assert identifier not in databases
            databases[identifier] = dict(
                NAME=kwgs.get("name", "postgres"),
                USER=kwgs.get("user", "postgres"),
                PASSWORD=kwgs.get("password", "postgres"),
                HOST=kwgs["host"],
                PORT=kwgs.get("port", "5432"),
                ENGINE="django.db.backends.postgresql",
                TIME_ZONE="UTC",
                USE_TZ=True,
            )
            ACTIVE_STORES[identifier] = DjangoStore(identifier)
    else:
        raise NotImplementedError(flavor)


def set_file_backend(media_root: Path) -> None:
    django_config()
    settings.MEDIA_ROOT = media_root
    setting_changed.send(None, setting="MEDIA_ROOT")


@contextlib.contextmanager
def django_setup(identifier: str) -> tp.Iterator[dict[str, tp.Any]]:
    django_config()

    assert identifier != "default"
    databases = settings.DATABASES
    yield databases
    new_apps = set(BACKEND_LINKER.app_labels) - set(settings.INSTALLED_APPS)
    if new_apps:
        for app_label in BACKEND_LINKER.app_labels:
            if app_label in new_apps:
                settings.INSTALLED_APPS.append(app_label)

        apps.apps_ready = apps.models_ready = apps.loading = apps.ready = False
        apps.clear_cache()
        apps.populate(settings.INSTALLED_APPS)
        setting_changed.send(None, setting="INSTALLED_APPS")

        try:
            with contextlib.redirect_stdout(io.StringIO()):
                call_command("makemigrations", "--noinput")
        except SystemExit:
            call_command("makemigrations")

    connections.configure_settings(databases)
    with contextlib.redirect_stdout(io.StringIO()):
        call_command("migrate", database=identifier)


def django_config() -> None:
    if not settings.configured:
        settings.configure(
            DATABASES={"default": {"ENGINE": "django.db.backends.dummy"}},
            TIME_ZONE="UTC",
            USE_TZ=True,
            DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        )
        settings.STORAGES["default"] = dict(BACKEND="admem.DirectoryFSS")
        django.setup()


def set_store_for_django(identifier: str = "default") -> None:
    ACTIVE_STORES[identifier] = DjangoStore(identifier)
