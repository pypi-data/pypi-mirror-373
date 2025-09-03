import datetime

import time_machine
from django.conf import (
    settings,
)
from django.db.models.query_utils import (
    DeferredAttribute,
)
from django.test.runner import (
    DiscoverRunner,
)
from django.test.utils import (
    override_settings,
)

from behave_bo.__main__ import (
    run_behave,
)
from behave_bo.behave_django_bo.consts import (
    override_settings_prefix,
    replace_current_date_prefix,
)
from behave_bo.behave_django_bo.utils import (
    override_current_date,
    override_dirs,
)
from behave_bo.configuration import (
    Configuration,
)
from behave_bo.loggers import (
    tests_logger,
)
from behave_bo.model import (
    Scenario,
)
from behave_bo.reporter.failed_tags import (
    FailedTagsParallelReporter,
    FailedTagsReporter,
)
from behave_bo.reporter.junit import (
    JUnitReporter,
)
from behave_bo.runner import (
    BehaveRunner,
    BehaveTagsCachedRunner,
    ParallelBehaveRunner,
)


behave_run_scenario = Scenario.run


class PatchedScenario(Scenario):

    @property
    def override_settings_tag(self):
        override_settings_tag = None

        for tag in self.tags:
            if tag.startswith(override_settings_prefix):
                override_settings_tag = tag
                break

        return override_settings_tag

    def make_override_settings_dict(self, runner) -> dict:
        """Формирует словарь настроек для переопределения в override_settings.

        Настройки, задаваемые в runner.override_settings_dict, будут переопределены
        или дополнены для конкретного сценария.

        Args:
            runner: объект класса Runner, исполнителя behave-автотестов.

        Returns:
            Словарь вида {Наименование настройки: значение}.

        """
        override_settings_dict = getattr(runner, 'override_settings_dict', {})

        if self.override_settings_tag:
            settings_string = self.override_settings_tag.removeprefix(override_settings_prefix)
            for key, value in map(lambda s: s.split('=', 1), settings_string.split(',')):
                if value.isdigit():
                    value = int(value)
                elif value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                elif value.lower() == 'none':
                    value = None

                override_settings_dict[key] = value

            tests_logger.info(
                f'Для сценария {self.main_tag} будут переопределены django settings: {override_settings_dict}'
            )

        return override_settings_dict

    @property
    def replace_current_date_tag(self):
        """Определение тега замены текущей даты у сценария."""
        replace_current_date_tag = None

        for tag in self.tags:
            if tag.startswith(replace_current_date_prefix):
                replace_current_date_tag = tag
                break

        return replace_current_date_tag

    def get_scenario_current_date(self) -> datetime.date:
        """Получение даты из тега замены текущей даты сценария.

        Returns:
            Объект даты
        """
        replace_current_date = None

        if self.replace_current_date_tag:
            replace_current_date = datetime.datetime.strptime(
                self.replace_current_date_tag.removeprefix(replace_current_date_prefix).split('=')[1],
                '%d.%m.%Y',
            ).date()

            tests_logger.info(
                f'Для сценария {self.main_tag} будут переопределена текущая дата: {replace_current_date:%d.%m.%Y}'
            )

        return replace_current_date

    def run_scenario(self, runner):
        """Пропатченный метод запуска behave-сценария.

        Сразу проверяется необходимость выполнения сценария, и если не нужно выполнять, помечается пропущенным.
        Если нужно выполнять, на время выполнения конкретного сценария создаёт уникальную временную директорию.

        Args:
            self: объект класса Scenario
            runner: объект класса Runner, исполнителя behave-автотестов.
        """
        failed = False
        should_run_scenario = self.should_run(runner.config)

        if should_run_scenario:
            for number, step in enumerate(self.steps, 1):
                step.number = number
            settings_dict = self.make_override_settings_dict(runner)
            scenario_current_date = self.get_scenario_current_date()

            with override_dirs(self), override_settings(**settings_dict), override_current_date(scenario_current_date):
                failed = behave_run_scenario(self, runner)
        else:
            self.mark_skipped()

        return failed


Scenario.base_skip_tags = list(Scenario.base_skip_tags) + [override_settings_prefix]
Scenario.override_settings_tag = PatchedScenario.override_settings_tag
Scenario.replace_current_date_tag = PatchedScenario.replace_current_date_tag
Scenario.make_override_settings_dict = PatchedScenario.make_override_settings_dict
Scenario.get_scenario_current_date = PatchedScenario.get_scenario_current_date
Scenario.run = PatchedScenario.run_scenario


class BaseBehaveTestRunner(DiscoverRunner):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.return_code_success = 0
        self.behave_config = None

        if kwargs.get('save_db'):
            # В случае если нужно сохранить результат в БД / отдельную БД,
            # атрибут keepdb должен быть True
            self.keepdb = True

    def get_tempdir_path(self):
        raise NotImplementedError

    def get_template_data_types(self):
        raise NotImplementedError

    def get_environment_filepath(self):
        raise NotImplementedError

    def run_behave_tests(self, behave_args, options):
        """Выполняет запуск behave тестов.

        Args:
            behave_args: Аргументы, относящиеся к behave_bo.
            options: Все аргументы команды запуска.

        Returns:
            Результат выполнения тестов.

        """
        self.behave_config = Configuration(behave_args)
        try:
            log_capture_exclude_template = settings.WEB_BB_BEHAVE__LOG_CAPTURE_EXCLUDE_TEMPLATE
        except AttributeError:
            log_capture_exclude_template = ''

        self.behave_config.log_capture_exclude_template = log_capture_exclude_template

        self._add_extra_parameters_to_behave_config(options)

        traveller = None

        if self.behave_config.replace_current_date:
            traveller = time_machine.travel(self.behave_config.replace_current_date)
            traveller.start()

        if self.parallel:
            behave_runner_class = ParallelBehaveRunner
            failed_tags_reporter_class = FailedTagsParallelReporter
        else:
            if self.behave_config.optimize_steps_loading:
                behave_runner_class = BehaveTagsCachedRunner
            else:
                behave_runner_class = BehaveRunner
            failed_tags_reporter_class = FailedTagsReporter

        failed_tags_reporter = failed_tags_reporter_class(self.behave_config)
        self.behave_config.reporters.append(failed_tags_reporter)

        try:
            junit_reporter = [r for r in self.behave_config.reporters if isinstance(r, JUnitReporter)][0]
        except IndexError:
            junit_reporter = None

        runner_kwargs = {
            'tempdir': self.get_tempdir_path(),
            'step_template_data_types': self.get_template_data_types(),
            'environment_filepath': self.get_environment_filepath(),
            'test_runner': self,
        }

        run_result = run_behave(
            self.behave_config,
            runner_class=behave_runner_class,
            runner_kwargs=runner_kwargs,
        )

        while failed_tags_reporter.rerun_required():
            failed_tags_reporter.rerun_up()
            tests_logger.info(
                f'Перезапуск упавших сценариев для выявления ложных падений '
                f'среди {len(failed_tags_reporter.main_run_failed_tags)} сценариев: '
                f'{", ".join(failed_tags_reporter.main_run_failed_tags)} '
                f'(попытка №{failed_tags_reporter.rerun_attempt})...\n'
            )

            if junit_reporter:
                junit_reporter.rerun = True
                self.behave_config.reporters.append(junit_reporter)

            run_behave(
                self.behave_config,
                runner_class=behave_runner_class,
                runner_kwargs=runner_kwargs,
            )

            if failed_tags_reporter.check_all_false_positive():
                run_result = self.return_code_success

        if traveller:
            traveller.stop()

        return run_result

    def _add_extra_parameters_to_behave_config(self, options):
        """Добавляет дополнительные параметры в конфиг в соответствии с options.

        Args:
            options: Аргументы команды запуска.

        """
        config = self.behave_config
        config.django_test_runner = self

        config.parallel = options.get('parallel')
        config.parallel_count = options.get('parallel_count')
        config.collect_top_scenarios = options.get('collect_top_scenarios')
        config.save_db = options.get('save_db')
        config.optimize_steps_loading = options.get('optimize_steps_loading')
        config.clear_cached_step_locations = options.get('clear_cached_step_locations')
        config.optimize_features_steps_loading = options.get('optimize_features_steps_loading')
        config.in_tags_order = options.get('in_tags_order')
        config.rerun_if_failed = options.get('rerun_if_failed')
        config.rerun_attempts = options.get('rerun_attempts')
        config.measure_requests_coverage = options.get('measure_requests_coverage')
        config.replace_current_date = None

        if options.get('replace_current_date'):
            try:
                config.replace_current_date = datetime.datetime.strptime(options['replace_current_date'], '%d.%m.%Y')
                tests_logger.info(
                    f'Запуск автотестов с заменой текущей даты на {config.replace_current_date:%d.%m.%Y}'
                )
            except ValueError as e:
                tests_logger.warning(f'Некорректное значение для параметра replace_current_date: {e}')

        config.save_changes_to_db = bool(config.save_db)

        return config


def _DeferredAttributeWithCheck__get__(self, instance, cls=None):
    """
    Добавление проверки/логирования в метод отложенного получения значения атрибута.

    Args:
        self: экземпляр класса DeferredAttribute
        instance: экземпляр класса модели для которого выполняется получение значения атрибута.
        cls: класс модели

    Returns:
        Значение атрибута.

    Raises:
        Исключение в случае если включена настройка CHECK_DEFERRED_ATTR_GET
         и значение атрибута не найдено в кэше, а значит его планируется получить из БД выполнив дополнительный запрос.
    """
    if instance is None:
        return self
    data = instance.__dict__
    field_name = self.field.attname

    if field_name in data:
        return data[field_name]

    attr = f"{instance.__class__.__name__}.{field_name}"
    message = f"Lazy fetching of {attr} may cause 1+N issue"

    if settings.WEB_BB_BEHAVE__CHECK_DEFERRED_ATTR_GET:
        raise AssertionError(message)
    elif settings.WEB_BB_BEHAVE__LOG_DEFERRED_ATTR_GET:
        tests_logger.warning(message)

    return DeferredAttribute__get(self, instance, cls)


DeferredAttribute__get, DeferredAttribute.__get__ = DeferredAttribute.__get__, _DeferredAttributeWithCheck__get__
