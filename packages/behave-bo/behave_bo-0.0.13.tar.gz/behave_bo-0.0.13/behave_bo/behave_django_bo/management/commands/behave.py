import argparse
import multiprocessing
import sys

from behave_bo.behave_django_bo.enums import (
    SaveDbParameterEnum,
)
from behave_bo.behave_django_bo.utils import (
    get_features_paths,
)
from behave_bo.configuration import (
    options as behave_options,
)
from django.conf import (
    settings,
)
from django.core.cache import (
    DEFAULT_CACHE_ALIAS,
    cache,
)
from django.core.management.base import (
    BaseCommand,
)
from django.test.signals import (
    clear_cache_handlers,
)
from django.test.utils import (
    get_runner,
)


def set_default_cache_backend():
    """Указание BehaveLocMemCache в качестве cache-backend по-молчанию если задана настройка."""
    if settings.WEB_BB_BEHAVE__USE_LOC_MEM_CACHE:
        settings.CACHES[DEFAULT_CACHE_ALIAS] = {
            'BACKEND': 'behave_bo.behave_django_bo.cache.BehaveLocMemCache',
            'LOCATION': '',
            'OPTIONS': {
                'MAX_ENTRIES': 500,
            },
        }


def positive_int(value):
    """Пользовательский тип функции для Argparse для обеспечения аргумента является позитивным целым числом."""
    try:
        ivalue = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid integer.")
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f"'{value}' must be a positive integer.")
    return ivalue


def add_command_arguments(parser):
    """
    Additional command line arguments for the behave management command

    @param parser: ArgumentParser для парсинга аргументов команды
    """
    parser.add_argument(
        '--use-existing-database',
        action='store_true',
        default=False,
        help="Don't create a test database. USE AT YOUR OWN RISK!",
    )
    parser.add_argument(
        '-k', '--keepdb',
        action='store_true',
        default=False,
        help="Preserves the test DB between runs.",
    )
    parser.add_argument(
        '-S', '--simple',
        action='store_true',
        default=False,
        help="Use simple test runner that supports Django's"
             " testing client only (no web browser automation)"
    )
    parser.add_argument(
        '--all',
        action='store_true',
        default=False,
        help='Discover tests in all apps and plugins and run them',
    )
    parser.add_argument(
        '--plugins',
        action='store',
        metavar='PLUGINS',
        dest='plugins',
        help='Enable runner plugins (comma separated)',
    )
    parser.add_argument(
        '--plugin_vars',
        action='store',
        metavar='VARS',
        dest='plugin_vars',
        help='Plugin variables',
    )
    parser.add_argument(
        '--disable_failed_plugin',
        action='store_true',
        dest='disable_failed_plugin',
        help='Disables plugin if it failed',
    )
    parser.add_argument(
        '--parallel',
        action='store_true',
        default=False,
        help='Run behave tests using up to N parallel processes, which can be set with --parallel-count.',
    )
    parser.add_argument(
        '--parallel-count',
        default=multiprocessing.cpu_count(),
        type=int,
        help='Parallel processes count.',
    )
    parser.add_argument(
        '--save-db',
        action='store',
        choices=SaveDbParameterEnum.values,
        help='Save changes by autotest to default db or separate db',
    )
    parser.add_argument(
        '--bgjob-wait-time',
        action='store',
        default=180,
        type=int,
        help='BackgroundJob wait cycle timeout in seconds.',
    )
    parser.add_argument(
        '--bgjob-wait-iteration-freeze',
        action='store',
        default=0.5,
        type=float,
        help='BackgroundJob wait iteration delay in seconds.',
    )
    parser.add_argument(
        '--generate-fixture',
        action='store',
        default='off',
        help='Generate fixtures for tests: "off": don\'t generate fixtures; '
             '"generate-only": only generate fixtures '
             'without execute behave tests; '
             '"generate": generate fixtures and execute behave tests.',
    )
    parser.add_argument(
        '--remove-readonly-requests',
        action='store_true',
        dest='remove_readonly_requests',
        default=False,
        help='Remove readonly requests files.',
    )
    parser.add_argument(
        '--skip-readonly-requests',
        action='store_true',
        default=False,
        help='Skip sending of readonly request (AppRequest) for non-check steps.',
    )
    parser.add_argument(
        '--skip-readonly-requests-url-endings',
        action='store',
        default='',
        help='Url endings for skip request (comma separated). Eg. /rows,/list',
    )
    parser.add_argument(
        '--skip-production-request-checks',
        action='store_true',
        default=False,
        help='Skip checking of production-request data.',
    )
    parser.add_argument(
        '--fix-checks',
        action='store_true',
        default=False,
        help='Fix failed autotests checks.',
    )
    parser.add_argument(
        '--fix-excluded-keys',
        action='store',
        default=None,
        help='Add all different keys to excluded_keys param.',
    )
    parser.add_argument(
        '--optimize-steps-loading',
        action='store_true',
        default=False,
        help='Using cached step locations. Subsequent runs are much faster '
             'for scenarios with already cached steps. Cleanup is recommended '
             'when changes are made to the location of step implementations. '
             'Use option "--clear-cached-step-locations" to clean up.',
    )
    parser.add_argument(
        '--optimize-features-steps-loading',
        action='store',
        default='',
        help='Указать путь до файла в котором будет сформирован кэш step_definitions по feature-файлам.'
             'Файл формируется при запуске без --parallel, а используется при запуске с --parallel.',
    )
    parser.add_argument(
        '--clear-cached-step-locations',
        action='store_true',
        default=False,
        help='Clearing cached step locations.',
    )
    parser.add_argument(
        '--analyze-model-records',
        action='store',
        default='',
        help='Use "ModelRecordAnalyzer" tool for specified scenarios.',
    )
    parser.add_argument(
        '--in-tags-order',
        action='store_true',
        default=False,
        help='Run scenarios in the order of specified tags in --tags.',
    )
    parser.add_argument(
        '--rerun-if-failed',
        action='store',
        default=0,
        type=int,
        help='Rerun failed tests if the number of failed tests does not exceed '
             'the specified value. 0 means rerun will not occur.',
    )
    parser.add_argument(
        '--rerun-attempts',
        action='store',
        default=1,
        type=positive_int,
        help='Count of rerun failed tests attempts.',
    )
    parser.add_argument(
        '--measure-requests-coverage',
        action='store_true',
        dest='measure_requests_coverage',
        default=False,
        help='Enable context switching per request.',
    )
    parser.add_argument(
        '--log-non-200-requests',
        action='store_true',
        default=False,
        dest='log_non_200_requests',
        help='Enable logging requests with non 200 status code.',
    )
    parser.add_argument(
        '--collect-top-scenarios',
        action='store_true',
        default=False,
        dest='collect_top_scenarios',
        help='Create top_scenarios.html in junit_directory',
    )
    parser.add_argument(
        '--replace-current-date',
        action='store',
        default='',
        help='Patch current_date with chosen value.',
    )


def add_behave_arguments(parser):  # noqa
    """
    Additional command line arguments extracted directly from behave
    """

    # Option strings that conflict with Django
    conflicts = [
        '--no-color',
        '--version',
        '-c',
        '-k',
        '-v',
        '-S',
        '--simple',
    ]

    parser.add_argument(
        'paths',
        action='store',
        nargs='*',
        help="Feature directory, file or file location (FILE:LINE)."
    )

    for fixed, keywords in behave_options:
        keywords = keywords.copy()

        # Configfile only entries are ignored
        if not fixed:
            continue

        # Build option strings
        option_strings = []
        for option in fixed:
            # Prefix conflicting option strings with `--behave`
            if option in conflicts:
                prefix = '--' if option.startswith('--') else '-'
                option = option.replace(prefix, '--behave-', 1)

            option_strings.append(option)

        # config_help isn't a valid keyword for add_argument
        if 'config_help' in keywords:
            keywords['help'] = keywords['config_help']
            del keywords['config_help']

        parser.add_argument(*option_strings, **keywords)


class Command(BaseCommand):
    help = 'Runs behave tests'
    requires_system_checks = False

    def add_arguments(self, parser):
        """
        Add behave's and our command line arguments to the command
        """
        parser.usage = "%(prog)s [options] [ [DIR|FILE|FILE:LINE] ]+"
        parser.description = """\
        Run a number of feature tests with behave_bo."""

        add_command_arguments(parser)
        add_behave_arguments(parser)

    def handle(self, *args, **options):
        set_default_cache_backend()

        # импортируем класс раннера, который указан в настройках
        django_test_runner_cls = get_runner(settings)

        django_test_runner = django_test_runner_cls(**options)
        django_test_runner.setup_test_environment()

        django_test_runner.collect_reset_sequences_sql()

        behave_args = self.get_behave_args()

        feature_paths = []

        if options['all']:
            feature_paths = get_features_paths()

        if not feature_paths:
            sys.exit()

        behave_args.extend(feature_paths)

        self.prerun_checks(options)

        django_test_runner.setup_plugins(behave_args, options)

        exit_status = django_test_runner.run_behave_tests(behave_args, options)

        # Teardown django environment
        django_test_runner.teardown_test_environment()

        if exit_status != 0:
            sys.exit(exit_status)

    def prerun_checks(self, options):
        """
        Выполнить проверки перед запуском
        """
        try:
            cache_backend = settings.CACHES[DEFAULT_CACHE_ALIAS]['BACKEND']
            cache_backend = cache_backend.rpartition('.')[2]
        except KeyError:
            cache_backend = None

        if options['parallel'] and cache_backend == 'RedisCache':
            redis_db_count = cache.client.connect().config_get('databases')['databases']
            clear_cache_handlers(setting='CACHES')
            cpu_thread_count = multiprocessing.cpu_count()

            if int(redis_db_count) < cpu_thread_count:
                raise Exception(
                    'При параллельном запуске тестов с использование redis в качестве кэша '
                    'количество бд redis должно быть больше или равно количеству потоков процессора.\n'
                    f'redis_db_count: {redis_db_count}, cpu_thread_count: {cpu_thread_count}'
                )

    def get_behave_args(self, argv=sys.argv):
        """
        Get a list of those command line arguments specified with the
        management command that are meant as arguments for running behave_bo.
        """
        parser = BehaveArgsHelper().create_parser('manage.py', 'behave')
        args, unknown = parser.parse_known_args(argv[2:])

        behave_args = []
        for option in unknown:
            # Remove behave prefix
            if option.startswith('--behave-'):
                option = option.replace('--behave-', '', 1)
                prefix = '-' if len(option) == 1 else '--'
                option = prefix + option

            behave_args.append(option)

        return behave_args


class BehaveArgsHelper(Command):

    def add_arguments(self, parser):
        """
        Override setup of command line arguments to make behave commands not
        be recognized. The unrecognized args will then be for behave! :)
        """
        add_command_arguments(parser)
