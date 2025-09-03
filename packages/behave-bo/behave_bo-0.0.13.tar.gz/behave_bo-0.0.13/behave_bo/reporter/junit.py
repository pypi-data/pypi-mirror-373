# pylint: disable=line-too-long
"""
This module provides a reporter with JUnit XML output.

Mapping of behave_bo model elements to XML elements::

    feature     -> xml_element:testsuite
    scenario    -> xml_element:testcase

XML document structure::

    # -- XML elements:
    # CARDINALITY SUFFIX:
    #   ?   optional (zero or one)
    #   *   many0 (zero or more)
    #   +   many (one or more)
    testsuites := sequence<testsuite>
    testsuite:
        properties? : sequence<property>
        testcase* :
            error?      : text
            failure?    : text
            system-out  : text
            system-err  : text

    testsuite:
        @name       : TokenString
        @tests      : int
        @failures   : int
        @errors     : int
        @skipped    : int
        @time       : Decimal       # Duration in seconds
        # -- SINCE: behave_bo-1.2.6
        @timestamp  : IsoDateTime
        @hostname   : string

    testcase:
        @name       : TokenString
        @classname  : TokenString
        @status     : string        # Status enum
        @time       : Decimal       # Elapsed seconds

    error:
        @message    : string
        @type       : string

    failure:
        @message    : string
        @type       : string

    # -- HINT: Not used
    property:
        @name  : TokenString
        @value : string

    type Status : Enum("passed", "failed", "skipped", "untested")

Note that a spec for JUnit XML output was not clearly defined.
Best sources are:

* `JUnit XML`_ (for PDF)
* JUnit XML (`ant spec 1`_, `ant spec 2`_)


.. _`JUnit XML`:  http://junitpdfreport.sourceforge.net/managedcontent/PdfTranslation
.. _`ant spec 1`: https://github.com/windyroad/JUnit-Schema
.. _`ant spec 2`: http://svn.apache.org/repos/asf/ant/core/trunk/src/main/org/apache/tools/ant/taskdefs/optional/junit/XMLJUnitResultFormatter.java
"""
# pylint: enable=line-too-long

import codecs
import os
import os.path
import re
import traceback
from datetime import (
    datetime,
)
from functools import (
    partial,
)
from xml.etree import (
    ElementTree,
)

import requests
from django.template import (
    Template,
    Context,
)
from lxml import (
    etree,
)

from behave_bo.consts import (
    scenario_group_prefix,
)
from behave_bo.formatter import (
    ansi_escapes,
)
from behave_bo.model import (
    Scenario,
    ScenarioOutline,
    Step,
)
from behave_bo.model_core import (
    Status,
)
from behave_bo.model_describe import (
    ModelDescriptor,
)
from behave_bo.reporter.base import (
    Reporter,
)
from behave_bo.textutil import (
    indent,
    make_indentation,
    text as _text,
)
from behave_bo.userdata import (
    UserDataNamespace,
)


def CDATA(text=None):   # pylint: disable=invalid-name
    # -- issue #70: remove_ansi_escapes(text)
    element = ElementTree.Element('![CDATA[')
    element.text = ansi_escapes.strip_escapes(text)
    return element


class ElementTreeWithCDATA(ElementTree.ElementTree):
    # pylint: disable=redefined-builtin, no-member
    def _write(self, file, node, encoding, namespaces):
        """This method is for ElementTree <= 1.2.6"""

        if node.tag == '![CDATA[':
            text = node.text.encode(encoding)
            file.write(f"\n<![CDATA[{text}]]>\n")
        else:
            ElementTree.ElementTree._write(self, file, node, encoding,
                                           namespaces)


if hasattr(ElementTree, '_serialize'):
    # pylint: disable=protected-access

    def _serialize_xml3(write, elem, qnames, namespaces,
                        short_empty_elements=None,
                        orig=ElementTree._serialize_xml):
        if elem.tag == '![CDATA[':
            write("\n<{tag}{text}]]>\n".format(
                tag=elem.tag, text=elem.text))
            return
        if short_empty_elements:
            # python >=3.3
            return orig(write, elem, qnames, namespaces, short_empty_elements)
        else:
            # python <3.3
            return orig(write, elem, qnames, namespaces)

    ElementTree._serialize_xml = ElementTree._serialize['xml'] = _serialize_xml3


class FeatureReportData:
    """
    Provides value object to collect JUnit report data from a Feature.
    """
    def __init__(self, feature, filename, classname=None):
        if not classname and filename:
            classname = filename.replace('/', '.')
        self.feature = feature
        self.filename = filename
        self.classname = classname
        self.testcases = []
        self.counts_tests = 0
        self.counts_errors = 0
        self.counts_failed = 0
        self.counts_skipped = 0

    def reset(self):
        self.testcases = []
        self.counts_tests = 0
        self.counts_errors = 0
        self.counts_failed = 0
        self.counts_skipped = 0


class JUnitReporter(Reporter):
    """Generates JUnit-like XML test report for behave_bo.
    """
    # -- XML REPORT:
    userdata_scope = "behave_bo.reporter.junit"
    show_timings = True     # -- Show step timings.
    show_skipped_always = False
    show_timestamp = True
    show_hostname = True
    # -- XML REPORT PART: Describe scenarios
    show_scenarios = ''   # Show particular scenarios descriptions.
    show_all_scenarios = True   # Show all scenarios descriptions.
    show_tags = True
    show_multiline = True
    build_url = ''

    def __init__(self, config):
        super().__init__(config)
        self.rerun = False
        self._features_failed_suites = {}
        self.setup_with_userdata(config.userdata)

    def setup_with_userdata(self, userdata):
        """Setup JUnit reporter with userdata information.
        A user can now tweak the output format of this reporter.

        EXAMPLE:
        .. code-block:: ini

            # -- FILE: behave_bo.ini
            [behave_bo.userdata]
            behave_bo.reporter.junit.show_hostname = false
        """
        # -- EXPERIMENTAL:
        config = UserDataNamespace(self.userdata_scope, userdata)
        self.show_hostname = config.getbool("show_hostname", self.show_hostname)
        self.show_multiline = config.getbool("show_multiline", self.show_multiline)
        self.show_all_scenarios = config.getbool("show_all_scenarios", self.show_all_scenarios)

        show_scenarios_str = config.get("show_scenarios", '')
        if show_scenarios_str:
            self.show_scenarios = show_scenarios_str.split(',')
        else:
            self.show_scenarios = []

        self.show_tags = config.getbool("show_tags", self.show_tags)
        self.show_timings = config.getbool("show_timings", self.show_timings)
        self.show_timestamp = config.getbool("show_timestamp", self.show_timestamp)
        self.show_skipped_always = config.getbool("show_skipped_always", self.show_skipped_always)

        if 'build_url' in userdata:
            self.build_url = userdata['build_url']

    def make_feature_filename(self, feature):
        """Пропатчено для формирования короткого имени файла в отчете.

        А в случае параллельного запуска тестов, если в тегах передан тег группы - добавляет к имени фичи постфикс
        чтобы потом собрать из нескольких файлов JUNIT-xml для feature - один файл JUNIT-xml.

        Args:
            self: Объект класса JUnitReporter.
            feature: Объект класса Feature.

        """
        feature_name = feature.location.filename
        base_name = os.path.basename(feature_name).split('.', 1)[0]

        if feature_name.startswith('plugins/'):
            plugin = feature_name.split('/')[1]
            base_name = f'{plugin}.{base_name}'

        if hasattr(self.config, 'group_number'):
            base_name += f'_{scenario_group_prefix}{self.config.group_number}'

        return base_name

    @property
    def show_skipped(self):
        return self.config.show_skipped or self.show_skipped_always

    # -- REPORTER-API:
    def feature(self, feature):
        if feature.status == Status.skipped and not self.show_skipped:
            # -- SKIP-OUTPUT: If skipped features should not be shown.
            return

        feature_filename = self.make_feature_filename(feature)
        classname = feature_filename
        report = FeatureReportData(feature, feature_filename)
        now = datetime.now()
        testcase_by_name = {}

        suite = ElementTree.Element('testsuite')
        feature_name = (feature.name or feature_filename).replace('.', '')
        suite.set('name', f'{classname}.{feature_name}')

        # -- BUILD-TESTCASES: From scenarios
        for scenario in feature:
            if isinstance(scenario, ScenarioOutline):
                scenario_outline = scenario
                self._process_scenario_outline(scenario_outline, report)
            else:
                self._process_scenario(scenario, report)

        # -- ADD TESTCASES to testsuite:
        for testcase in report.testcases:
            suite.append(testcase)

            if not self.config.parallel and self.rerun:
                testcase_by_name[testcase.attrib[JunitXMLAttrsEnum.NAME]] = testcase

        suite.set('tests', _text(report.counts_tests))
        suite.set('errors', _text(report.counts_errors))
        suite.set('failures', _text(report.counts_failed))
        suite.set('skipped', _text(report.counts_skipped))  # WAS: skips
        suite.set('time', _text(round(feature.duration, 6)))
        # -- SINCE: behave_bo-1.2.6.dev0
        if self.show_timestamp:
            suite.set('timestamp', _text(now.isoformat()))
        if self.show_hostname:
            suite.set('hostname', _text(gethostname()))

        if self.build_url:
            suite.set('build_url', self.build_url)

        if not os.path.exists(self.config.junit_directory):
            # -- ENSURE: Create multiple directory levels at once.
            os.makedirs(self.config.junit_directory)

        if not self.config.parallel:
            if feature_name in self._features_failed_suites and self.rerun:
                prev_suite = self._features_failed_suites[feature_name]
                prev_suite.set('failures', _text(suite.attrib['failures']))

                for tc in prev_suite:
                    if tc.attrib[JunitXMLAttrsEnum.STATUS] != JunitXMLAttrsEnum.FAILED:
                        continue

                    rerun_tc = testcase_by_name[tc.attrib[JunitXMLAttrsEnum.NAME]]

                    for attr in (
                        JunitXMLAttrsEnum.STATUS,
                        JunitXMLAttrsEnum.TIME,
                        JunitXMLAttrsEnum.TIME_PROCESS,
                        JunitXMLAttrsEnum.PID,
                    ):
                        tc.attrib[attr] = rerun_tc.attrib[attr]

                suite = prev_suite

            elif report.counts_failed > 0 or report.counts_errors > 0:
                self._features_failed_suites[feature_name] = suite

        tree = ElementTreeWithCDATA(suite)
        report_dirname = self.config.junit_directory
        report_basename = f'TESTS-{feature_filename}.xml'
        report_filename = os.path.join(report_dirname, report_basename)
        tree.write(codecs.open(report_filename, "wb"), "UTF-8")

    # -- MORE:
    # pylint: disable=line-too-long
    @staticmethod
    def select_step_with_status(status, steps):
        """Helper function to find the first step that has the given
        step.status.

        EXAMPLE: Search for a failing step in a scenario (all steps).
            >>> scenario = ...
            >>> failed_step = select_step_with_status(Status.failed, scenario)
            >>> failed_step = select_step_with_status(Status.failed, scenario.all_steps)
            >>> assert failed_step.status == Status.failed

        EXAMPLE: Search only scenario steps, skip background steps.
            >>> failed_step = select_step_with_status(Status.failed, scenario.steps)

        :param status:  Step status to search for (as enum value).
        :param steps:   List of steps to search in (or scenario).
        :returns: Step object, if found.
        :returns: None, otherwise.

        .. versionchanged:: 1.2.6
            status: Use enum value instead of string (or string).
        """
        for step in steps:
            assert isinstance(step, Step), f"TYPE-MISMATCH: step.class={step.__class__.__name__}"
            if step.status == status:
                return step
        # -- OTHERWISE: No step with the given status found.
        # KeyError("Step with status={0} not found".format(status))
        return None
    # pylint: enable=line-too-long

    def describe_step(self, step):
        status_text = _text(step.status.name)
        if self.show_timings:
            status_text += f' in {step.duration:.3f}s (pt {step.duration_pt:.3f}s)'
        text = f'{step.keyword} {step.name} ... '
        text += f'{status_text}\n'
        if self.show_multiline:
            prefix = make_indentation(2)
            if step.text:
                text += ModelDescriptor.describe_docstring(step.text, prefix)
            elif step.table:
                text += ModelDescriptor.describe_table(step.table, prefix)
        return text

    @classmethod
    def describe_tags(cls, tags):
        text = ''
        if tags:
            text = '@' + ' @'.join(tags)
        return text

    def describe_scenario(self, scenario):
        """Describe the scenario and the test status.
        NOTE: table, multiline text is missing in description.

        :param scenario:  Scenario that was tested.
        :return: Textual description of the scenario.
        """
        header_line = '\n@scenario.begin\n'
        if self.show_tags and scenario.tags:
            header_line += f'\n  {self.describe_tags(scenario.tags)}\n'

        header_line += f'  {scenario.keyword}: {scenario.name}\n'
        footer_line = '\n@scenario.end\n' + '-' * 80 + '\n'
        text = ''
        for step in scenario:
            text += self.describe_step(step)
        step_indentation = make_indentation(4)
        return header_line + indent(text, step_indentation) + footer_line

    def _process_scenario(self, scenario, report):
        """Process a scenario and append information to JUnit report object.
        This corresponds to a JUnit testcase:

          * testcase.@classname = f(filename) +'.'+ feature.name
          * testcase.@name   = scenario.name
          * testcase.@status = scenario.status
          * testcase.@time   = scenario.duration

        Distinguishes now between failures and errors.
        Failures are AssertationErrors: expectation is violated/not met.
        Errors are unexpected RuntimeErrors (all other exceptions).

        If a failure/error occurs, the step, that caused the failure,
        and its location are provided now.

        :param scenario:  Scenario to process.
        :param report:    Context object to store/add info to (outgoing param).
        """
        # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        assert isinstance(scenario, Scenario)
        assert not isinstance(scenario, ScenarioOutline)
        if scenario.status != Status.skipped or self.show_skipped:
            # -- NOTE: Count only if not-skipped or skipped should be shown.
            report.counts_tests += 1
        classname = report.classname
        feature = report.feature
        feature_name = feature.name
        if not feature_name:
            feature_name = self.make_feature_filename(feature)

        feature_name = feature_name.replace('.', '')

        case = ElementTree.Element('testcase')
        case.set("classname", f"{classname}.{feature_name}")
        case.set("name", scenario.name_w_tag or "")
        case.set("status", scenario.status.name)
        case.set("time", _text(round(scenario.duration, 6)))
        case.set("time_process", _text(round(scenario.duration_pt, 6)))
        case.set("pid", f'{os.getpid()}')

        step = None
        failing_step = None
        if scenario.status == Status.failed:
            for status in (Status.failed, Status.undefined):
                step = self.select_step_with_status(status, scenario)
                if step:
                    break
            # -- NOTE: Scenario may fail now due to hook-errors.
            element_name = "failure"
            if step and isinstance(step.exception, (AssertionError, type(None))):
                # -- FAILURE: AssertionError
                assert step.status in (Status.failed, Status.undefined)
                report.counts_failed += 1
            else:
                # -- UNEXPECTED RUNTIME-ERROR:
                report.counts_errors += 1
                element_name = "error"
            # -- COMMON-PART:
            failure = ElementTree.Element(element_name)
            if step:
                step_text = self.describe_step(step).rstrip()
                text = f"\nFailing step: {step_text}\nLocation: {step.location}\n"
                message = _text(step.exception)
                failure.set('type', step.exception.__class__.__name__)
                failure.set('message', message)
                text += _text(step.error_message)
            else:
                # -- MAYBE: Hook failure before any step is executed.
                failure_type = "UnknownError"
                if scenario.exception:
                    failure_type = scenario.exception.__class__.__name__
                failure.set('type', failure_type)
                failure.set('message', scenario.error_message or "")
                traceback_lines = traceback.format_tb(scenario.exc_traceback)
                traceback_lines.insert(0, "Traceback:\n")
                text = _text("".join(traceback_lines))
            failure.append(CDATA(text))
            case.append(failure)
        elif (scenario.status in (Status.skipped, Status.untested)
              and self.show_skipped):
            report.counts_skipped += 1
            step = self.select_step_with_status(Status.undefined, scenario)
            if step:
                # -- UNDEFINED-STEP:
                report.counts_failed += 1
                failure = ElementTree.Element("failure")
                failure.set("type", "undefined")
                failure.set("message", f"Undefined Step: {step.name}")
                case.append(failure)
            else:
                skip = ElementTree.Element('skipped')
                case.append(skip)

        # Create stdout section for each test case
        stdout = ElementTree.Element("system-out")
        text = ""
        if self.show_all_scenarios or scenario.main_tag in self.show_scenarios:
            text = self.describe_scenario(scenario)

        # Append the captured standard output
        if scenario.captured.stdout:
            output = _text(scenario.captured.stdout)
            text += f"\nCaptured stdout:\n{output}\n"
        stdout.append(CDATA(text))
        case.append(stdout)

        # Create stderr section for each test case
        if scenario.captured.stderr:
            stderr = ElementTree.Element("system-err")
            output = _text(scenario.captured.stderr)
            text = f"\nCaptured stderr:\n{output}\n"
            stderr.append(CDATA(text))
            case.append(stderr)

        if scenario.status != Status.skipped or self.show_skipped:
            report.testcases.append(case)

    def _process_scenario_outline(self, scenario_outline, report):
        assert isinstance(scenario_outline, ScenarioOutline)
        for scenario in scenario_outline:
            assert isinstance(scenario, Scenario)
            self._process_scenario(scenario, report)


class JunitXMLAttrsEnum:
    """
    Перечисление атрибутов тега testsuite
    """

    ERRORS_COUNT = 'errors'
    FAILURES_COUNT = 'failures'
    SKIPPED_COUNT = 'skipped'
    TESTS_COUNT = 'tests'
    TIME = 'time'
    TIME_PROCESS = 'time_process'
    PID = 'pid'
    TIMESTAMP = 'timestamp'
    NAME = 'name'
    HOSTNAME = 'hostname'
    BUILD_URL = 'build_url'
    STATUS = 'status'
    UNTESTED = 'untested'
    FAILED = 'failed'

    NUMERIC_ATTRIBUTES = (
        ERRORS_COUNT,
        FAILURES_COUNT,
        SKIPPED_COUNT,
        TESTS_COUNT,
        TIME,
        TIME_PROCESS,
    )


class JunitReportsCombiner:
    """
    Объединитель частей Junit-отчётов в один файл.
    """

    def __init__(
        self,
        reports_dir_path,
        html_report_destination_path=None,
        tests_execution_start_time=None,
        rerun=False,
    ) -> None:
        """
        @param tests_execution_start_time: Время начала выполнения тестов.
            Нужно для расчёта времени выполнения тест-сьюта.
        @param reports_dir_path: путь к директории с xml-файлами junit-отчётов
        """
        super().__init__()

        if tests_execution_start_time:
            self._tests_execution_start_time = tests_execution_start_time
        else:
            self._tests_execution_start_time = datetime.now()

        self._reports_dir_path = reports_dir_path
        self._html_report_destination_path = html_report_destination_path or self._reports_dir_path
        self._rerun = rerun

        self._reports_data = {}
        self._reports_parts_data = {}
        self._reports_files = []
        self._reports_parts_files = []

        self._scenario_group_name_pattern = fr'_{scenario_group_prefix}\d+'
        self._report_part_filename_pattern = fr'(.*?){self._scenario_group_name_pattern}\.xml'  # noqa
        self._report_filename_pattern = fr'(.*?)\.xml'  # noqa

        self._suite_attrs_with_parsers = {
            JunitXMLAttrsEnum.ERRORS_COUNT: int,
            JunitXMLAttrsEnum.FAILURES_COUNT: int,
            JunitXMLAttrsEnum.SKIPPED_COUNT: int,
            JunitXMLAttrsEnum.TESTS_COUNT: int,
            JunitXMLAttrsEnum.HOSTNAME: str,
            JunitXMLAttrsEnum.BUILD_URL: str,
            JunitXMLAttrsEnum.TIMESTAMP: lambda date_str: datetime.fromisoformat(date_str),
            JunitXMLAttrsEnum.NAME: partial(
                re.sub,
                self._scenario_group_name_pattern,
                '',
            ),
        }

        self._test_cases_with_time = []

    def prepare_report_files_paths(self):
        """
        Сформировать набор файлов частей junit-отчётов
        """
        for _, _, files in os.walk(self._reports_dir_path, topdown=False):
            for filename in files:
                match_part = re.match(self._report_part_filename_pattern, filename)
                match_report = re.match(self._report_filename_pattern, filename)

                if match_part:
                    self._reports_parts_files.append(
                        (
                            match_part.group(1),
                            os.path.join(self._reports_dir_path, filename),
                        )
                    )
                elif match_report:
                    self._reports_files.append(
                        (
                            match_report.group(1),
                            os.path.join(self._reports_dir_path, filename),
                        )
                    )

    def collect_reports_data_from_files(self, files, data):
        """
        Получить данные о junit-отчётах из xml-файлов
        """
        for feature_name, path in files:
            tree = etree.parse(path)
            suite_xml_root = tree.getroot()

            if feature_name not in data:
                data[feature_name] = {
                    'suite': {},
                    'test_cases': [],
                }

            test_suite = data[feature_name]['suite']

            for attr, parser in self._suite_attrs_with_parsers.items():
                value = parser(suite_xml_root.attrib.get(attr, 0))

                if attr not in test_suite:
                    test_suite[attr] = value
                elif attr == JunitXMLAttrsEnum.TIMESTAMP:
                    if test_suite[attr] < value:
                        test_suite[attr] = value
                elif attr in JunitXMLAttrsEnum.NUMERIC_ATTRIBUTES:
                    test_suite[attr] += value

            data[feature_name]['test_cases'].extend(
                tree.iter('testcase')
            )

    def prepare_tc_url(self, build_url, test_case):
        """
        Сформировать url-адрес тесткейса в тестовом отчёте.
        """
        feature_file_path = requests.utils.quote(test_case.attrib.get('classname', '').replace('.', '/'))
        scenario_path = re.sub(r'[^\w0-9]', '_', test_case.attrib.get(JunitXMLAttrsEnum.NAME, ''))
        return f'{build_url}testReport/{feature_file_path}/{scenario_path}/'

    def export_reports_parts_data_to_files(self):
        """
        Записать полученные данные о junit-отчётах в xml-файлы junit-отчётов
        """
        reports_paths = []
        name_parser = self._suite_attrs_with_parsers[JunitXMLAttrsEnum.NAME]

        for feature_filename, data in self._reports_parts_data.items():
            suite = etree.Element('testsuite')

            for attr, _ in self._suite_attrs_with_parsers.items():
                suite.set(attr, str(data['suite'].get(attr)))

            last_suite_timestamp = data['suite'].get(JunitXMLAttrsEnum.TIMESTAMP)  # noqa
            duration = last_suite_timestamp - self._tests_execution_start_time
            suite.set(JunitXMLAttrsEnum.TIME, str(duration.total_seconds()))
            build_url = data['suite'].get(JunitXMLAttrsEnum.BUILD_URL)

            for test_case in data['test_cases']:
                if test_case.attrib[JunitXMLAttrsEnum.STATUS] == JunitXMLAttrsEnum.UNTESTED:
                    continue

                raw_classname = test_case.attrib.get('classname', '')

                classname = name_parser(raw_classname)
                test_case.set('classname', classname)

                tc_url = ''

                for child in test_case:
                    child.text = etree.CDATA(child.text)
                    if child.text.strip():
                        tc_url = self.prepare_tc_url(build_url, test_case)

                suite.append(test_case)

                self._test_cases_with_time.append(
                    (
                        round(float(test_case.attrib.get(JunitXMLAttrsEnum.TIME, 0)), 2),
                        round(float(test_case.attrib.get(JunitXMLAttrsEnum.TIME_PROCESS, 0)), 2),
                        test_case.attrib.get(JunitXMLAttrsEnum.NAME, ''),
                        test_case.attrib.get(JunitXMLAttrsEnum.STATUS, ''),
                        test_case.attrib.get(JunitXMLAttrsEnum.PID, ''),
                        tc_url,
                    )
                )

            report_file_path = os.path.join(
                self._reports_dir_path,
                f'{feature_filename}.xml',
            )
            tree = etree.ElementTree(suite)
            tree.write(
                report_file_path,
                encoding='UTF-8',
            )
            reports_paths.append(report_file_path)

        return reports_paths

    def remove_reports_parts_files(self):
        """
        Удаляет файлы частей Junit-отчётов.
        Они не нужны, т.к. были объединены в общий файл junit-отчёта.
        """
        for _, path in self._reports_parts_files:
            if os.path.exists(path):
                os.remove(path)

    def change_reports_parts_rerun_data(self):
        """
        Использует в качестве данных для выгрузки данные из ранее сформированных xml-файлов,
        вносит в них исправления с учётом перезапуска упавших тестов.
        """
        self.collect_reports_data_from_files(
            files=self._reports_files,
            data=self._reports_data,
        )

        for feature_filename, data in self._reports_parts_data.items():
            reports_data = self._reports_data[feature_filename]
            reports_data['suite'][JunitXMLAttrsEnum.FAILURES_COUNT] = data['suite'][JunitXMLAttrsEnum.FAILURES_COUNT]

            for tc in reports_data['test_cases']:
                if tc.attrib[JunitXMLAttrsEnum.STATUS] != JunitXMLAttrsEnum.FAILED:
                    continue

                for rerun_tc in data['test_cases']:
                    if (
                        tc.attrib[JunitXMLAttrsEnum.NAME] == rerun_tc.attrib[JunitXMLAttrsEnum.NAME]
                        and rerun_tc.attrib[JunitXMLAttrsEnum.STATUS] != JunitXMLAttrsEnum.UNTESTED
                    ):
                        for attr in (
                            JunitXMLAttrsEnum.STATUS,
                            JunitXMLAttrsEnum.TIME,
                            JunitXMLAttrsEnum.TIME_PROCESS,
                            JunitXMLAttrsEnum.PID,
                        ):
                            tc.attrib[attr] = rerun_tc.attrib[attr]
                        break

            self._reports_parts_data[feature_filename] = reports_data

    def join_reports(self):
        """
        Собрать данные отчётов из файлов.
        Объединить части junit-отчётов полученные при выполнении параллельных процессов.
        Если это режим перезапуска, внести исправления в junit-отчёты по итогу перезапуска.
        Удалить файлы частей junit-отчётов.
        """
        self.prepare_report_files_paths()
        self.collect_reports_data_from_files(
            files=self._reports_parts_files,
            data=self._reports_parts_data,
        )

        if self._rerun:
            self.change_reports_parts_rerun_data()

        reports_paths = self.export_reports_parts_data_to_files()

        self.remove_reports_parts_files()

        return reports_paths

    def export_top_scenarios_by_time(self):
        if self._rerun:
            # не выполняем формирования файла топ запросов если в режиме перезапуска
            return

        testcases = []

        for time, time_process, tc_name, tc_status, tc_pid, tc_url in sorted(self._test_cases_with_time, key=lambda k: k[0], reverse=True):
            testcases.append({
                'name': tc_name,
                'status': tc_status,
                'pid': tc_pid,
                'url': tc_url,
                'time': time,
                'time_process': time_process,
            })

        with open(os.path.join(os.path.dirname(__file__), 'templates/autotests_report_template.html')) as ft:
            django_template = Template(ft.read())

        rendered_data = django_template.render(Context({
            'title': 'Список автотестов по времени выполнения',
            'page_type': 'top_scenarios',
            'testcases': testcases,
        }))

        with open(os.path.join(self._html_report_destination_path, f'top_scenarios.html'), 'w') as f:
            f.write(rendered_data)

    def export_html_report(self):
        """Формирует html-отчёт из junit-файлов
        """
        self.prepare_report_files_paths()
        self.collect_reports_data_from_files(
            files=self._reports_files,
            data=self._reports_data,
        )

        with open(os.path.join(os.path.dirname(__file__), 'templates/autotests_report_template.html')) as ft:
            django_template = Template(ft.read())

        total_count = 0
        failed_data = []

        for suite_data in self._reports_data.values():
            try:
                suite_name = suite_data['suite']['name'].split('.', 1)[1]
                suite_data['suite']['name'] = suite_name
            except:
                pass

            tested_test_cases = []

            for test_case in suite_data['test_cases']:
                tc_main_tag = test_case.attrib['name'].split(' ', 1)[0]
                test_case.attrib['main_tag'] = tc_main_tag

                if test_case.attrib[JunitXMLAttrsEnum.STATUS] == JunitXMLAttrsEnum.UNTESTED:
                    continue
                elif test_case.attrib[JunitXMLAttrsEnum.STATUS] == JunitXMLAttrsEnum.FAILED:
                    failed_data.append(test_case)
                    try:
                        failure_text = test_case.find('failure').text
                    except:
                        failure_text = 'текст ошибки недоступен'

                    try:
                        failure_text = test_case.find('error').text
                    except:
                        pass

                    test_case.attrib['failure_text'] = failure_text

                total_count += 1
                tested_test_cases.append(test_case)

            suite_data['test_cases'] = tested_test_cases

        now = datetime.now()

        try:
            from web_bb.core.base.helpers import version_info
            version = sorted(version_info(check_installed_apps=False), key=lambda el: el['name'] == 'web_bb_app', reverse=True)
        except Exception as e:
            print(f'Ошибка при формировании информации о версии: {e}')
            version = None

        rendered_data = django_template.render(Context({
            'title': f'Результат автотестирования {now}',
            'page_type': 'autotest_result',
            'total_count': total_count,
            'failed_data': failed_data,
            'suites_data': self._reports_data.values(),
            'version_info': version,
        }))

        export_path = os.path.join(self._html_report_destination_path, f'autotests_report_{now}.html')
        with open(export_path, 'w') as f:
            f.write(rendered_data)

        return export_path

# -----------------------------------------------------------------------------
# SUPPORT:
# -----------------------------------------------------------------------------
def gethostname():
    """Return hostname of local host (as string)"""
    import socket
    return socket.gethostname()
