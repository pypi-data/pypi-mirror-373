import os
import shutil
import tempfile
import uuid
from contextlib import (
    contextmanager,
)

import time_machine
from django.apps import (
    apps,
)
from django.conf import (
    settings,
)
from django.test.utils import (
    override_settings,
)


def get_features_paths():
    """Возвращает список путей до директорий features в app'ах, если существуют."""

    paths = []
    for app in apps.get_app_configs():
        features_dir = os.path.join(app.path, 'features')
        if os.path.isdir(features_dir):
            paths.append(features_dir)

    return paths


@contextmanager
def override_dirs(scenario):
    """Контекстный менеджер для создания уникальных директорий под временные файлы и downloads для выполняемого сценария

    Args:
        scenario: объект класса Scenario

    """
    prefix = scenario.main_tag if scenario.tags else uuid.uuid4().hex[:6]

    old_tempdir = settings.TEMPDIR
    old_downloads_dir = settings.DOWNLOADS_DIR

    new_tempdir = f"{old_tempdir}/{prefix}__{scenario.line}"
    new_downloads_dir = f"{old_downloads_dir}/{prefix}__{scenario.line}"

    if os.path.isdir(new_tempdir):
        shutil.rmtree(new_tempdir, ignore_errors=True)

    tempfile.tempdir = new_tempdir

    if not os.path.isdir(tempfile.gettempdir()):
        os.makedirs(tempfile.gettempdir())

    if os.path.isdir(new_downloads_dir):
        shutil.rmtree(new_downloads_dir, ignore_errors=True)

    if not os.path.isdir(new_downloads_dir):
        os.makedirs(new_downloads_dir)

    try:
        with override_settings(TEMPDIR=new_tempdir, DOWNLOADS_DIR=new_downloads_dir):
            yield
    finally:
        tempfile.tempdir = old_tempdir


@contextmanager
def override_current_date(selected_date):
    """Контекстный менеджер для подмены текущей даты

    Args:
        selected_date: дата на которую требуется подменить текущую дату
    """
    try:
        if selected_date:
            with time_machine.travel(selected_date):
                yield
        else:
            yield
    finally:
        pass
