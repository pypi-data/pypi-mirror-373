import json
import os
import sys
from datetime import (
    datetime,
    timedelta,
)
from typing import (
    Iterable,
)

from django.conf import (
    settings,
)

from behave_bo.configuration import (
    Configuration,
)
from behave_bo.formatter.base import (
    StreamOpener,
)
from behave_bo.formatter.progress import (
    ScenarioStepProgressFormatter,
)
from behave_bo.model import (
    ScenarioOutline,
)
from behave_bo.model_core import (
    Status,
)
from behave_bo.reporter.base import (
    Reporter,
)
from behave_bo.tag_expression import (
    TagExpression,
)


class FalsePositiveTestsReport:
    """
    Класс для обработки информации по ложным падениям тестов.
    """

    def __init__(self, build_url: str = ''):
        self.is_opened = False

        self.build_url = build_url
        self.date_format = '%Y-%m-%d'
        self.storage_period = timedelta(days=60)

        self.report_file_path = settings.WEB_BB_BEHAVE__FALSE_POSITIVE_TESTS_INFO
        self.report = {}

    def open(self, actualize_file: bool = False):
        """Открывает файл с отчетом.

        Args:
            actualize_file: Выполнить актуализацию содержимого файла в соответствии с периодом хранения.
        """
        if not self.is_opened:
            if os.path.exists(self.report_file_path):
                with open(self.report_file_path) as f:
                    self.report = json.load(f)

            if self.report and actualize_file:
                self._actualize()
                self._save()

            self.is_opened = True

    def update_and_save(self, tags: Iterable):
        """Обновляет информацию о ложных падениях и сохраняет в файл.

        Args:
            tags: Список тегов.
        """
        if tags:
            self._update(tags)
            self._save()

    def _update(self, tags: Iterable):
        """Обновляет информацию о ложных падениях.

        Args:
            tags: Список тегов.
        """
        current_date_string = datetime.today().strftime(self.date_format)

        for tag in tags:
            if tag in self.report:
                self.report[tag]['count'] += 1
                self.report[tag]['failures'].setdefault(
                    current_date_string,
                    []
                ).append(self.build_url)
            else:
                self.report[tag] = {
                    'count': 1,
                    'failures': {
                        current_date_string: [self.build_url],
                    },
                }

    def _is_storage_expired(self, date_string: str) -> bool:
        """Проверяет, истек ли срок хранения информации по переданной дате.

        Args:
            date_string: Строковое представление даты заданного формата.

        Returns:
            Результат проверки.
        """

        return datetime.today() - datetime.strptime(date_string, self.date_format) > self.storage_period

    def _actualize(self):
        """Актуализирует информацию в соответствии с периодом хранения.

        Удаляет информацию по тесту, если дата последнего падения больше заданного срока хранения.
        Удаляет ссылки на сборки по тесту, если дата падения больше заданного срока хранения.
        """
        expired_tags = set()
        for tag, info in self.report.items():
            failure_dates = sorted(info['failures'])

            if self._is_storage_expired(failure_dates[-1]):
                expired_tags.add(tag)
            else:
                for date_string in failure_dates:
                    if self._is_storage_expired(date_string):
                        info['failures'].pop(date_string)
                    else:
                        break

                info['count'] = sum([len(list_of_urls) for list_of_urls in info['failures'].values()])

        for tag in expired_tags:
            self.report.pop(tag)

    def _save(self):
        """Сохраняет информацию о ложных падениях в файл."""
        try:
            if os.path.exists(self.report_file_path):
                with open(self.report_file_path, 'w') as f:
                    f.writelines(json.dumps(self.report))
        except Exception as e:
            print(f'Не удалось сохранить информацию о ложных падениях в файл: {e}')


class FailedTagsReporter(Reporter):
    """
    Репортер выводящий в лог список тегов сценариев упавших автотестов разделённых запятой.
    """

    def __init__(self, config: Configuration):
        super().__init__(config)
        stream = getattr(sys, "stdout", sys.stderr)
        self.stream = StreamOpener.ensure_stream_with_encoder(stream)
        self.failed_tags = set()
        self.rerun_attempt = 0
        self._main_run_failed_tags = set()
        self.false_positive_tests_amount = None

        self.false_positive_tests_report = FalsePositiveTestsReport(
            build_url=config.userdata.get('build_url', ''),
        )

    @property
    def main_run_failed_tags(self):
        """Теги упавших тестов основного прогона."""

        return self._main_run_failed_tags if self.is_in_rerun_mode else self.failed_tags

    @property
    def false_positive_tags(self) -> set:
        """Теги тестов с ложными падениями."""

        return self._main_run_failed_tags.difference(self.failed_tags) if self.is_in_rerun_mode else set()

    @property
    def is_in_rerun_mode(self):
        """Выполняется перезапуск команды автотестов."""
        return self.rerun_attempt > 0

    def rerun_required(self) -> bool:
        """Возвращает результат проверки условий перезапуска."""

        return (
            self.config.rerun_if_failed and
            self.failed_tags and
            len(self.failed_tags) <= self.config.rerun_if_failed and
            self.rerun_attempt < self.config.rerun_attempts
        )

    def rerun_up(self):
        """Выполняет настройки перед запуском упавших сценариев."""
        self.config.rerun = True
        self.rerun_attempt += 1
        self.config.tags = TagExpression([','.join(self.failed_tags)])
        self.config.reporters = [self]
        self.config.format = [ScenarioStepProgressFormatter.name]

        self._main_run_failed_tags = self.failed_tags
        self.failed_tags = set()
        self.false_positive_tests_report.open(actualize_file=True)

    def log_failed_tags(self):
        """Выводит информацию об упавших тестах в виде списка тегов."""
        self.stream.write(f"\nFailing scenarios tags: {','.join(self.main_run_failed_tags)}\n")
        if self.is_in_rerun_mode:
            self.false_positive_tests_amount = len(self.false_positive_tags) if self.failed_tags else 'All'
            self.stream.write(f"{self.false_positive_tests_amount} false-positive: {','.join(self.false_positive_tags)}\n")

            if self.failed_tags:
                self.stream.write(f"{len(self.failed_tags)} actual failed: {','.join(self.failed_tags)}\n")

        self.stream.write("\n")

    def feature(self, feature):
        for scenario in feature:
            if isinstance(scenario, ScenarioOutline):
                self.process_scenario_outline(scenario)
            else:
                self.process_scenario(scenario)

    def end(self):
        if self.failed_tags or self.is_in_rerun_mode:
            self.log_failed_tags()
            if self.false_positive_tags:
                self.false_positive_tests_report.update_and_save(self.false_positive_tags)

    def process_scenario(self, scenario):
        if scenario.status == Status.failed:
            self.failed_tags.add(f'{scenario.main_tag}')

    def process_scenario_outline(self, scenario_outline):
        for scenario in scenario_outline.scenarios:
            self.process_scenario(scenario)

    def check_all_false_positive(self):
        return self.false_positive_tests_amount == 'All'


class FailedTagsParallelReporter(FailedTagsReporter):
    """
    Репортер выводящий в лог список тегов сценариев упавших автотестов разделённых запятой адаптированный
    для запуска в параллельных процессах.
    """
    process_kwarg_name = 'failed_tags_proxy_list'
    failed_tags_proxy_list = None

    def init_process_variable(self, manager):
        """Инициализирует атрибут для хранения списка тегов.

        Args:
            manager: multiprocessing.Manager
        """
        self.failed_tags_proxy_list = manager.list()

        return self.failed_tags_proxy_list

    def end(self):
        if self.failed_tags:
            self.failed_tags_proxy_list.append(self.failed_tags)

    def after_parallel_run(self):
        if self.failed_tags_proxy_list or self.is_in_rerun_mode:
            self.failed_tags.update(*self.failed_tags_proxy_list)
            self.log_failed_tags()
            if self.false_positive_tags:
                self.false_positive_tests_report.update_and_save(self.false_positive_tags)
