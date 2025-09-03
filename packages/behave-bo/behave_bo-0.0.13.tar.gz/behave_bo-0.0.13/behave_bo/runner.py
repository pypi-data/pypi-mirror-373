"""
This module provides Runner class to run behave_bo feature files (or model elements).
"""

import contextlib
import datetime
import itertools
import json
import multiprocessing
import os
import os.path
import random
import sys
import traceback
import warnings
import weakref
from functools import (
    cached_property,
)
from glob import (
    glob,
)

from behave_bo import (
    register_type,
)
from behave_bo._types import (
    ExceptionUtil,
)
from behave_bo.capture import (
    CaptureController,
)
from behave_bo.configuration import (
    ConfigError,
)
from behave_bo.consts import (
    scenario_group_prefix,
)
from behave_bo.formatter._registry import (
    make_formatters,
)
from behave_bo.loggers import (
    tests_logger,
)
from behave_bo.matchers import (
    CaseSensitiveParser,
    ParseMatcher,
)
from behave_bo.reporter.junit import (
    JunitReportsCombiner,
)
from behave_bo.runner_util import (
    PathManager,
    collect_feature_locations,
    exec_file,
    load_step_modules,
    parse_features,
)
from behave_bo.step_registry import (
    registry as the_step_registry,
)


class CleanupError(RuntimeError):
    pass


class ContextMaskWarning(UserWarning):
    """Raised if a context variable is being overwritten in some situations.

    If the variable was originally set by user code then this will be raised if
    *behave_bo* overwites the value.

    If the variable was originally set by *behave_bo* then this will be raised if
    user code overwites the value.
    """
    pass


class Context:
    """Hold contextual information during the running of tests.

    This object is a place to store information related to the tests you're
    running. You may add arbitrary attributes to it of whatever value you need.

    During the running of your tests the object will have additional layers of
    namespace added and removed automatically. There is a "root" namespace and
    additional namespaces for features and scenarios.

    Certain names are used by *behave_bo*; be wary of using them yourself as
    *behave_bo* may overwrite the value you set. These names are:

    .. attribute:: feature

      This is set when we start testing a new feature and holds a
      :class:`~behave_bo.model.Feature`. It will not be present outside of a
      feature (i.e. within the scope of the environment before_all and
      after_all).

    .. attribute:: scenario

      This is set when we start testing a new scenario (including the
      individual scenarios of a scenario outline) and holds a
      :class:`~behave_bo.model.Scenario`. It will not be present outside of the
      scope of a scenario.

    .. attribute:: tags

      The current set of active tags (as a Python set containing instances of
      :class:`~behave_bo.model.Tag` which are basically just glorified strings)
      combined from the feature and scenario. This attribute will not be
      present outside of a feature scope.

    .. attribute:: aborted

      This is set to true in the root namespace when the user aborts a test run
      (:exc:`KeyboardInterrupt` exception). Initially: False.

    .. attribute:: failed

      This is set to true in the root namespace as soon as a step fails.
      Initially: False.

    .. attribute:: table

      This is set at the step level and holds any :class:`~behave_bo.model.Table`
      associated with the step.

    .. attribute:: text

      This is set at the step level and holds any multiline text associated
      with the step.

    .. attribute:: config

      The configuration of *behave_bo* as determined by configuration files and
      command-line options. The attributes of this object are the same as the
      `configuration file section names`_.

    .. attribute:: active_outline

      This is set for each scenario in a scenario outline and references the
      :class:`~behave_bo.model.Row` that is active for the current scenario. It is
      present mostly for debugging, but may be useful otherwise.

    .. attribute:: log_capture

      If logging capture is enabled then this attribute contains the captured
      logging as an instance of :class:`~behave_bo.log_capture.LoggingCapture`.
      It is not present if logging is not being captured.

    .. attribute:: stdout_capture

      If stdout capture is enabled then this attribute contains the captured
      output as a StringIO instance. It is not present if stdout is not being
      captured.

    .. attribute:: stderr_capture

      If stderr capture is enabled then this attribute contains the captured
      output as a StringIO instance. It is not present if stderr is not being
      captured.

    If an attempt made by user code to overwrite one of these variables, or
    indeed by *behave_bo* to overwite a user-set variable, then a
    :class:`behave_bo.runner.ContextMaskWarning` warning will be raised.

    You may use the "in" operator to test whether a certain value has been set
    on the context, for example:

        "feature" in context

    checks whether there is a "feature" value in the context.

    Values may be deleted from the context using "del" but only at the level
    they are set. You can't delete a value set by a feature at a scenario level
    but you can delete a value set for a scenario in that scenario.

    .. _`configuration file section names`: behave_bo.html#configuration-files
    """
    # pylint: disable=too-many-instance-attributes
    BEHAVE = "behave_bo"
    USER = "user"
    FAIL_ON_CLEANUP_ERRORS = True

    def __init__(self, runner):
        self._runner = weakref.proxy(runner)
        self._config = runner.config
        d = self._root = {
            "aborted": False,
            "failed": False,
            "config": self._config,
            "active_outline": None,
            "cleanup_errors": 0,
            "@cleanups": [],  # -- REQUIRED-BY: before_all() hook
            "@layer": "testrun",
        }
        self._stack = [d]
        self._record = {}
        self._origin = {}
        self._mode = self.BEHAVE
        self.feature = None
        # -- RECHECK: If needed
        self.text = None
        self.table = None
        self.stdout_capture = None
        self.stderr_capture = None
        self.log_capture = None
        self.fail_on_cleanup_errors = self.FAIL_ON_CLEANUP_ERRORS

    @staticmethod
    def ignore_cleanup_error(context, cleanup_func, exception):
        pass

    @staticmethod
    def print_cleanup_error(context, cleanup_func, exception):
        cleanup_func_name = getattr(cleanup_func, "__name__", None)
        if not cleanup_func_name:
            cleanup_func_name = "%r" % cleanup_func
        print("CLEANUP-ERROR in %s: %s: %s" %
              (cleanup_func_name, exception.__class__.__name__, exception))
        traceback.print_exc(file=sys.stdout)
        # MAYBE: context._dump(pretty=True, prefix="Context: ")
        # -- MARK: testrun as FAILED
        # context._set_root_attribute("failed", True)

    def _do_cleanups(self):
        """Execute optional cleanup functions when stack frame is popped.
        A user can add a user-specified handler for cleanup errors.

        .. code-block:: python

            # -- FILE: features/environment.py
            def cleanup_database(database):
                pass

            def handle_cleanup_error(context, cleanup_func, exception):
                pass

            def before_all(context):
                context.on_cleanup_error = handle_cleanup_error
                context.add_cleanup(cleanup_database, the_database)
        """
        # -- BEST-EFFORT ALGORITHM: Tries to perform all cleanups.
        assert self._stack, "REQUIRE: Non-empty stack"
        current_layer = self._stack[0]
        cleanup_funcs = current_layer.get("@cleanups", [])
        on_cleanup_error = getattr(self, "on_cleanup_error",
                                   self.print_cleanup_error)
        context = self
        cleanup_errors = []
        for cleanup_func in reversed(cleanup_funcs):
            try:
                cleanup_func()
            except Exception as e:  # pylint: disable=broad-except
                # pylint: disable=protected-access
                context._root["cleanup_errors"] += 1
                cleanup_errors.append(sys.exc_info())
                on_cleanup_error(context, cleanup_func, e)

        if self.fail_on_cleanup_errors and cleanup_errors:
            first_cleanup_erro_info = cleanup_errors[0]
            del cleanup_errors  # -- ENSURE: Release other exception frames.

    def _push(self, layer_name=None):
        """Push a new layer on the context stack.
        HINT: Use layer_name values: "scenario", "feature", "testrun".

        :param layer_name:   Layer name to use (or None).
        """
        initial_data = {"@cleanups": []}
        if layer_name:
            initial_data["@layer"] = layer_name
        self._stack.insert(0, initial_data)

    def _pop(self):
        """Pop the current layer from the context stack.
        Performs any pending cleanups, registered for this layer.
        """
        try:
            self._do_cleanups()
        finally:
            # -- ENSURE: Layer is removed even if cleanup-errors occur.
            self._stack.pop(0)

    def _use_with_behave_mode(self):
        """Provides a context manager for using the context in BEHAVE mode."""
        return use_context_with_mode(self, Context.BEHAVE)

    def use_with_user_mode(self):
        """Provides a context manager for using the context in USER mode."""
        return use_context_with_mode(self, Context.USER)

    def _set_root_attribute(self, attr, value):
        for frame in self.__dict__["_stack"]:
            if frame is self.__dict__["_root"]:
                continue
            if attr in frame:
                record = self.__dict__["_record"][attr]
                params = {
                    "attr": attr,
                    "filename": record[0],
                    "line": record[1],
                    "function": record[3],
                }
                self._emit_warning(attr, params)

        self.__dict__["_root"][attr] = value
        if attr not in self._origin:
            self._origin[attr] = self._mode

    def _emit_warning(self, attr, params):
        msg = ""
        if self._mode is self.BEHAVE and self._origin[attr] is not self.BEHAVE:
            msg = "behave_bo runner is masking context attribute '%(attr)s' " \
                  "originally set in %(function)s (%(filename)s:%(line)s)"
        elif self._mode is self.USER:
            if self._origin[attr] is not self.USER:
                msg = "user code is masking context attribute '%(attr)s' " \
                      "originally set by behave_bo"
            elif self._config.verbose:
                msg = "user code is masking context attribute " \
                      "'%(attr)s'; see the tutorial for what this means"
        if msg:
            msg = msg % params
            warnings.warn(msg, ContextMaskWarning, stacklevel=3)

    def _dump(self, pretty=False, prefix="  "):
        for level, frame in enumerate(self._stack):
            print("%sLevel %d" % (prefix, level))
            if pretty:
                for name in sorted(frame.keys()):
                    value = frame[name]
                    print("%s  %-15s = %r" % (prefix, name, value))
            else:
                print(prefix + repr(frame))

    def __getattr__(self, attr):
        if attr[0] == "_":
            return self.__dict__[attr]
        for frame in self._stack:
            if attr in frame:
                return frame[attr]
        msg = "'{0}' object has no attribute '{1}'"
        msg = msg.format(self.__class__.__name__, attr)
        raise AttributeError(msg)

    def __setattr__(self, attr, value):
        if attr[0] == "_":
            self.__dict__[attr] = value
            return

        for frame in self._stack[1:]:
            if attr in frame:
                record = self._record[attr]
                params = {
                    "attr": attr,
                    "filename": record[0],
                    "line": record[1],
                    "function": record[3],
                }
                self._emit_warning(attr, params)

        stack_limit = 2
        stack_frame = traceback.extract_stack(limit=stack_limit)[0]
        self._record[attr] = stack_frame
        frame = self._stack[0]
        frame[attr] = value
        if attr not in self._origin:
            self._origin[attr] = self._mode

    def __delattr__(self, attr):
        frame = self._stack[0]
        if attr in frame:
            del frame[attr]
            del self._record[attr]
        else:
            msg = "'{0}' object has no attribute '{1}' at the current level"
            msg = msg.format(self.__class__.__name__, attr)
            raise AttributeError(msg)

    def __contains__(self, attr):
        if attr[0] == "_":
            return attr in self.__dict__
        for frame in self._stack:
            if attr in frame:
                return True
        return False

    def execute_steps(self, steps_text):
        """The steps identified in the "steps" text string will be parsed and
        executed in turn just as though they were defined in a feature file.

        If the execute_steps call fails (either through error or failure
        assertion) then the step invoking it will need to catch the resulting
        exceptions.

        :param steps_text:  Text with the Gherkin steps to execute (as string).
        :returns: True, if the steps executed successfully.
        :raises: AssertionError, if a step failure occurs.
        :raises: ValueError, if invoked without a feature context.
        """
        assert isinstance(steps_text, str), "Steps must be unicode."
        if not self.feature:
            raise ValueError("execute_steps() called outside of feature")

        # -- PREPARE: Save original context data for current step.
        # Needed if step definition that called this method uses .table/.text
        original_table = getattr(self, "table", None)
        original_text = getattr(self, "text", None)

        self.feature.parser.variant = "steps"
        steps = self.feature.parser.parse_steps(steps_text)
        with self._use_with_behave_mode():
            for step in steps:
                passed = step.run(self._runner, quiet=True, capture=False)
                if not passed:
                    # -- ISSUE #96: Provide more substep info to diagnose problem.
                    step_line = f"{step.keyword} {step.name}"
                    message = "%s SUB-STEP: %s" % \
                              (step.status.name.upper(), step_line)
                    if step.error_message:
                        message += "\nSubstep info: %s\n" % step.error_message
                        message += "Traceback (of failed substep):\n"
                        message += "".join(traceback.format_tb(step.exc_traceback))
                    # message += u"\nTraceback (of context.execute_steps()):"
                    assert False, message

            # -- FINALLY: Restore original context data for current step.
            self.table = original_table
            self.text = original_text
        return True

    def add_cleanup(self, cleanup_func, *args, **kwargs):
        """Adds a cleanup function that is called when :meth:`Context._pop()`
        is called. This is intended for user-cleanups.

        :param cleanup_func:    Callable function
        :param args:            Args for cleanup_func() call (optional).
        :param kwargs:          Kwargs for cleanup_func() call (optional).
        """
        # MAYBE:
        assert callable(cleanup_func), "REQUIRES: callable(cleanup_func)"
        assert self._stack
        if args or kwargs:
            def internal_cleanup_func():
                cleanup_func(*args, **kwargs)
        else:
            internal_cleanup_func = cleanup_func

        current_frame = self._stack[0]
        if cleanup_func not in current_frame["@cleanups"]:
            # -- AVOID DUPLICATES:
            current_frame["@cleanups"].append(internal_cleanup_func)


@contextlib.contextmanager
def use_context_with_mode(context, mode):
    """Switch context to BEHAVE or USER mode.
    Provides a context manager for switching between the two context modes.

    .. sourcecode:: python

        context = Context()
        with use_context_with_mode(context, Context.BEHAVE):
            ...     # Do something
        # -- POSTCONDITION: Original context._mode is restored.

    :param context:  Context object to use.
    :param mode:     Mode to apply to context object.
    """
    # pylint: disable=protected-access
    assert mode in (Context.BEHAVE, Context.USER)
    current_mode = context._mode
    try:
        context._mode = mode
        yield
    finally:
        # -- RESTORE: Initial current_mode
        #    Even if an AssertionError/Exception is raised.
        context._mode = current_mode


@contextlib.contextmanager
def scoped_context_layer(context, layer_name=None):
    """Provides context manager for context layer (push/do-something/pop cycle).

    .. code-block::

        with scoped_context_layer(context):
            the_fixture = use_fixture(foo, context, name="foo_42")
    """
    # pylint: disable=protected-access
    try:
        context._push(layer_name)
        yield context
    finally:
        context._pop()


def path_getrootdir(path):
    """
    Extract rootdir from path in a platform independent way.

    POSIX-PATH EXAMPLE:
        rootdir = path_getrootdir("/foo/bar/one.feature")
        assert rootdir == "/"

    WINDOWS-PATH EXAMPLE:
        rootdir = path_getrootdir("D:\\foo\\bar\\one.feature")
        assert rootdir == r"D:\"
    """
    drive, _ = os.path.splitdrive(path)
    if drive:
        # -- WINDOWS:
        return drive + os.path.sep
    # -- POSIX:
    return os.path.sep


class ModelRunner:
    """
    Test runner for a behave_bo model (features).
    Provides the core functionality of a test runner and
    the functional API needed by model elements.

    .. attribute:: aborted

          This is set to true when the user aborts a test run
          (:exc:`KeyboardInterrupt` exception). Initially: False.
          Stored as derived attribute in :attr:`Context.aborted`.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, config, features=None, step_registry=None):
        self.config = config
        self.features = features or []
        self.hooks = {}
        self.formatters = []
        self.undefined_steps = []
        self.step_registry = step_registry
        self.capture_controller = CaptureController(config)

        self.context = None
        self.feature = None
        self.hook_failures = 0

    # @property
    def _get_aborted(self):
        value = False
        if self.context:
            value = self.context.aborted
        return value

    # @aborted.setter
    def _set_aborted(self, value):
        # pylint: disable=protected-access
        assert self.context, "REQUIRE: context, but context=%r" % self.context
        self.context._set_root_attribute("aborted", bool(value))

    aborted = property(_get_aborted, _set_aborted,
                       doc="Indicates that test run is aborted by the user.")

    def run_hook(self, name, context, *args):
        if not self.config.dry_run and (name in self.hooks):
            try:
                with context.use_with_user_mode():
                    self.hooks[name](context, *args)
            # except KeyboardInterrupt:
            #     self.aborted = True
            #     if name not in ("before_all", "after_all"):
            #         raise
            except Exception as e:  # pylint: disable=broad-except
                # -- HANDLE HOOK ERRORS:
                use_traceback = False
                if self.config.verbose:
                    use_traceback = True
                    ExceptionUtil.set_traceback(e)
                extra = ""
                if "tag" in name:
                    extra = "(tag=%s)" % args[0]

                error_text = ExceptionUtil.describe(e, use_traceback).rstrip()
                error_message = f"HOOK-ERROR in {name}{extra}: {error_text}"
                print(error_message)
                self.hook_failures += 1
                if "tag" in name:
                    # -- SCENARIO or FEATURE
                    statement = getattr(context, "scenario", context.feature)
                elif "all" in name:
                    # -- ABORT EXECUTION: For before_all/after_all
                    self.aborted = True
                    statement = None
                else:
                    # -- CASE: feature, scenario, step
                    statement = args[0]

                if statement:
                    # -- CASE: feature, scenario, step
                    statement.hook_failed = True
                    if statement.error_message:
                        # -- NOTE: One exception/failure is already stored.
                        #    Append only error message.
                        statement.error_message += "\n" + error_message
                    else:
                        # -- FIRST EXCEPTION/FAILURE:
                        statement.store_exception_context(e)
                        statement.error_message = error_message

    def setup_capture(self):
        if not self.context:
            self.context = Context(self)
        self.capture_controller.setup_capture(self.context)

    def start_capture(self):
        self.capture_controller.start_capture()

    def stop_capture(self):
        self.capture_controller.stop_capture()

    def teardown_capture(self):
        self.capture_controller.teardown_capture()

    def should_run_feature(self, feature):
        """
        Проверка нужно ли запускать feature.
        """
        return True

    def pre_run_feature(self, feature):
        """Действия перед запуском feature"""
        pass

    def run_model(self, features=None):
        # pylint: disable=too-many-branches
        if not self.context:
            self.context = Context(self)
        if self.step_registry is None:
            self.step_registry = the_step_registry
        if features is None:
            features = self.features

        # -- ENSURE: context.execute_steps() works in weird cases (hooks, ...)
        context = self.context
        self.hook_failures = 0
        self.setup_capture()

        if not self.config.save_db or self.config.parallel:
            # Настроим отдельную БД (которая после завершения удаляется) и подключимся к ней.
            self.config.django_test_runner.setup_databases(
                db_postfix=str(os.getpid()),
            )

        self.run_hook("before_all", context)

        run_feature = not self.aborted
        failed_count = 0
        undefined_steps_initial_size = len(self.undefined_steps)
        for feature in features:
            if not self.should_run_feature(feature):
                # Если не нужно запускать feature, просто пропустим, чтобы не инициировать лишние вызовы reporters.
                continue

            if run_feature:
                try:
                    self.feature = feature
                    for formatter in self.formatters:
                        formatter.uri(feature.filename)

                    self.pre_run_feature(feature)
                    failed = feature.run(self)
                    if failed:
                        failed_count += 1
                        if self.config.stop or self.aborted:
                            # -- FAIL-EARLY: After first failure.
                            run_feature = False
                except KeyboardInterrupt:
                    self.aborted = True
                    failed_count += 1
                    run_feature = False

            # -- ALWAYS: Report run/not-run feature to reporters.
            # REQUIRED-FOR: Summary to keep track of untested features.
            for reporter in self.config.reporters:
                reporter.feature(feature)

        # -- AFTER-ALL:
        # pylint: disable=protected-access, broad-except
        cleanups_failed = False
        self.run_hook("after_all", self.context)
        try:
            self.context._do_cleanups()  # Without dropping the last context layer.
        except Exception:
            cleanups_failed = True

        if self.aborted:
            print("\nABORTED: By user.")
        for formatter in self.formatters:
            formatter.close()
        for reporter in self.config.reporters:
            reporter.end()

        failed = ((failed_count > 0) or self.aborted or (self.hook_failures > 0)
                  or (len(self.undefined_steps) > undefined_steps_initial_size)
                  or cleanups_failed)
        # XXX-MAYBE: or context.failed)
        return failed

    def run(self):
        """
        Implements the run method by running the model.
        """
        self.context = Context(self)
        return self.run_model()


class Runner(ModelRunner):
    """
    Standard test runner for behave_bo:

      * setup paths
      * loads environment hooks
      * loads step definitions
      * select feature files, parses them and creates model (elements)
    """

    def __init__(self, config, **kwargs):
        super().__init__(config)
        self.path_manager = PathManager()
        self.base_dir = None

    def setup_paths(self):
        # pylint: disable=too-many-branches, too-many-statements
        if self.config.paths:
            if self.config.verbose:
                print("Supplied path:",
                      ", ".join('"%s"' % path for path in self.config.paths))
            first_path = self.config.paths[0]
            if hasattr(first_path, "filename"):
                # -- BETTER: isinstance(first_path, FileLocation):
                first_path = first_path.filename
            base_dir = first_path
            if base_dir.startswith("@"):
                # -- USE: behave_bo @features.txt
                base_dir = base_dir[1:]
                file_locations = self.feature_locations()
                if file_locations:
                    base_dir = os.path.dirname(file_locations[0].filename)
            base_dir = os.path.abspath(base_dir)

            # supplied path might be to a feature file
            if os.path.isfile(base_dir):
                if self.config.verbose:
                    print("Primary path is to a file so using its directory")
                base_dir = os.path.dirname(base_dir)
        else:
            if self.config.verbose:
                print('Using default path "./features"')
            base_dir = os.path.abspath("features")

        # Get the root. This is not guaranteed to be "/" because Windows.
        root_dir = path_getrootdir(base_dir)
        new_base_dir = base_dir
        steps_dir = self.config.steps_dir
        environment_file = self.config.environment_file

        while True:
            if self.config.verbose:
                print("Trying base directory:", new_base_dir)

            if os.path.isdir(os.path.join(new_base_dir, steps_dir)):
                break
            if os.path.isfile(os.path.join(new_base_dir, environment_file)):
                break
            if new_base_dir == root_dir:
                break

            new_base_dir = os.path.dirname(new_base_dir)

        if new_base_dir == root_dir:
            if self.config.verbose:
                if not self.config.paths:
                    print('ERROR: Could not find "%s" directory. '
                          'Please specify where to find your features.' % steps_dir)
                else:
                    print('ERROR: Could not find "%s" directory in your '
                          'specified path "%s"' % (steps_dir, base_dir))

            message = f'No {steps_dir} directory in {base_dir!r}'
            raise ConfigError(message)

        base_dir = new_base_dir
        self.config.base_dir = base_dir

        for dirpath, dirnames, filenames in os.walk(base_dir):
            if [fn for fn in filenames if fn.endswith(".feature")]:
                break
        else:
            if self.config.verbose:
                if not self.config.paths:
                    print('ERROR: Could not find any "<name>.feature" files. '
                          'Please specify where to find your features.')
                else:
                    print('ERROR: Could not find any "<name>.feature" files '
                          'in your specified path "%s"' % base_dir)
            raise ConfigError('No feature files in %r' % base_dir)

        self.base_dir = base_dir
        self.path_manager.add(base_dir)
        if not self.config.paths:
            self.config.paths = [base_dir]

        if base_dir != os.getcwd():
            self.path_manager.add(os.getcwd())

    def before_all_default_hook(self, context):
        """
        Default implementation for :func:`before_all()` hook.
        Setup the logging subsystem based on the configuration data.
        """
        # pylint: disable=no-self-use
        context.config.setup_logging()

    def load_hooks(self, filename=None):
        filename = filename or self.config.environment_file
        hooks_path = os.path.join(self.base_dir, filename)
        if os.path.exists(hooks_path):
            exec_file(hooks_path, self.hooks)

        if "before_all" not in self.hooks:
            self.hooks["before_all"] = self.before_all_default_hook

    def load_step_definitions(self, extra_step_paths=None):
        if extra_step_paths is None:
            extra_step_paths = []
        # -- Allow steps to import other stuff from the steps dir
        # NOTE: Default matcher can be overridden in "environment.py" hook.
        steps_dir = os.path.join(self.base_dir, self.config.steps_dir)
        step_paths = [steps_dir] + list(extra_step_paths)
        load_step_modules(step_paths)

    def feature_locations(self):
        return collect_feature_locations(self.config.paths)

    def run(self):
        with self.path_manager:
            self.setup_paths()
            return self.run_with_paths()

    def run_with_paths(self):
        self.context = Context(self)
        self.load_hooks()
        self.load_step_definitions()

        # -- ENSURE: context.execute_steps() works in weird cases (hooks, ...)
        # self.setup_capture()
        # self.run_hook("before_all", self.context)

        # -- STEP: Parse all feature files (by using their file location).
        feature_locations = [filename for filename in self.feature_locations()
                             if not self.config.exclude(filename)]
        features = parse_features(feature_locations, language=self.config.lang)
        self.features.extend(features)

        # -- STEP: Run all features.
        stream_openers = self.config.outputs
        self.formatters = make_formatters(self.config, stream_openers)
        return self.run_model()


class BehaveRunner(Runner):
    """Раннер для запуска тестов.

    """

    def __init__(self, config, **kwargs):
        super().__init__(config)
        self.tempdir = kwargs.get('tempdir')
        self.step_template_data_types = kwargs.get('step_template_data_types', {})
        self.environment_filepath = kwargs.get('environment_filepath')
        self.test_runner = kwargs.get('test_runner')
        self.test_runner.behave_runner = self

    @cached_property
    def tag_scenario_map(self):
        """Словарь соответствия тэгов и сценариев.
        """
        tags_map = {}

        for feature in self.features:
            for scenario in feature.scenarios:
                if scenario.main_tag in tags_map:
                    raise Exception(f'Дублирование основного тега сценария {scenario.main_tag}')
                else:
                    tags_map[scenario.main_tag] = scenario

        return tags_map

    def get_step_locations(self, feature=None) -> set:
        """Получает список всех путей до директорий с определением шагов.

        Returns:
            Расположения реализаций шагов.
        """
        step_locations = set()

        for path in self.config.paths:
            steps_dir_path = os.path.join(path, self.config.steps_dir)
            if os.path.isdir(steps_dir_path):
                step_locations.add(steps_dir_path)

        return step_locations

    def do_register_types(self):
        """Зарегистрировать пользовательские типы парсинга параметров из шагов."""
        ParseMatcher.parser_class = CaseSensitiveParser

        register_type(**self.step_template_data_types)

    def load_step_definitions(self, extra_step_paths=None, feature=None):
        """Переопределен для загрузки шагов из всех app'ов и регистрации пользовательских типов.

        Args:
            extra_step_paths: Дополнительные пути до директорий с определением шагов.
            feature: Объект класса Feature.
        """
        self.do_register_types()
        step_locations = set(extra_step_paths or [])
        step_locations.update(self.get_step_locations(feature=feature))

        steps_dir = os.path.join(self.base_dir, self.config.steps_dir)
        step_locations.add(steps_dir)

        load_step_modules(step_locations)

    def get_filtered_feature_locations(self):
        """Получить подходящие пути до feature-файлов."""
        return [
            filename
            for filename in self.feature_locations()
            if not self.config.exclude(filename)
        ]

    def sort_scenarios_by_given_tags(self):
        """Сортирует сценарии в соответствии с переданными тэгами."""

        def sort_key(s):
            """Ключ сортировки сценариев."""

            return (given_tags.index(s.main_tag), True) if s.main_tag in given_tags else (0, False)

        given_tags = self.config.tags.ands[0]
        features = []
        for tag in given_tags:
            feature = self.tag_scenario_map[tag].feature
            if feature not in features:
                self.features.remove(feature)
                feature.scenarios = sorted(feature.scenarios, key=sort_key)
                features.append(feature)

        self.features = features + self.features

    def save_features_steps_definition_cache(self):
        with open(self.config.optimize_features_steps_loading, 'w') as f:
            f.write(json.dumps({
                f.filename: {
                    scenario: list(definitions)
                    for scenario, definitions in f.steps_definitions_dirs.items()
                } for f in self.features
            }))
            
        tests_logger.info(
            f"Файл кэширования feature-файлов экспортирован: {self.config.optimize_features_steps_loading}"
        )

    def run_with_paths(self):
        """Изменен порядок загрузки определения шагов и парсинга feature файлов.

        """
        self.context = Context(self)
        self.load_hooks(filename=self.environment_filepath)

        feature_locations = self.get_filtered_feature_locations()
        features = parse_features(feature_locations, language=self.config.lang)
        self.features.extend(features)

        if self.config.in_tags_order:
            self.sort_scenarios_by_given_tags()

        self.load_step_definitions()

        if self.config.optimize_features_steps_loading:
            self.config.dry_run = True
            failed = self.run_model()
            self.save_features_steps_definition_cache()
        else:
            stream_openers = self.config.outputs
            self.formatters = make_formatters(self.config, stream_openers)
            failed = self.run_model()

        return failed


class BehaveTagsCachedRunner(BehaveRunner):
    """
    Раннер тестов с возможностью кэшировать в файлы пути до steps/ по тегам отдельных сценариев,
    для ускорения загрузки load_step_definitions.
    """

    def __init__(self, config, **kwargs):
        self.not_cached_tags = set()
        super().__init__(config, **kwargs)

    def run_with_paths(self):
        if self.config.clear_cached_step_locations:
            self.clear_cached_steps_dir()

        return super().run_with_paths()

    def get_step_locations(self, feature=None) -> set:
        """Получает пути до директорий с определением шагов из кэша.
        Если в кеше сценарий не найден, для него создается запись.

        Returns:
            Расположения реализаций шагов.
        """
        step_locations = set()

        # Определение тегов, относящихся к сценариям.
        scenario_tags = set(self.tag_scenario_map).intersection(sum(self.config.tags.ands, []))

        self.not_cached_tags = scenario_tags.difference(self.cached_scenario_tags)

        if self.not_cached_tags:
            step_locations = super().get_step_locations(feature=feature)
        else:
            for tag in scenario_tags:
                step_locations.update(self.cached_step_locations[tag])

        return step_locations

    def load_step_definitions(self, extra_step_paths=None, feature=None):
        super().load_step_definitions(extra_step_paths, feature)
        self.save_step_locations_in_cache()

    @property
    def cached_steps_dir(self):
        """Директория хранения кэшированных путей реализации шагов.

        """
        temp_dir = os.path.join(self.tempdir, 'cached_step_locations')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        return temp_dir

    def clear_cached_steps_dir(self):
        """Очищает кэшированные пути шагов сценариев.

        """
        if self.cached_scenario_tags:
            for f in glob(os.path.join(self.cached_steps_dir, '*')):
                os.remove(f)
            tests_logger.info('Кэшированные пути шагов сценариев очищены.')
        else:
            tests_logger.info('Кэшированные пути шагов не найдены.')

        exit(0)

    @cached_property
    def cached_scenario_tags(self):
        """Тэги кэшированных путей сценариев.

        """
        return set(os.listdir(self.cached_steps_dir))

    @cached_property
    def cached_step_locations(self):
        """Словарь соответствия тэгов и кэшированных путей реализации шагов.

        """
        step_locations = {}

        for tag in self.cached_scenario_tags:
            path = os.path.join(self.cached_steps_dir, tag)
            if os.path.isfile(path):
                with open(path) as f:
                    locations_str = f.read()
                locations = json.loads(locations_str)
                step_locations[tag] = locations

        return step_locations

    def save_step_locations_in_cache(self) -> None:
        """Сохраняет пути реализации шагов для ещё не закэшированных тегов."""

        for tag in self.not_cached_tags:
            scenario = self.tag_scenario_map[tag]
            scenario_step_locations = set()
            scenario_has_undefined_steps = True

            for n, step in enumerate(scenario.all_steps):
                try:
                    location = the_step_registry.find_match(step).location.dirname()
                except AttributeError:
                    if scenario.type == 'scenario_outline':
                        step = list(scenario.scenarios[0].all_steps)[n]
                        try:
                            location = the_step_registry.find_match(step).location.dirname()
                        except AttributeError:
                            break
                    else:
                        break
                scenario_step_locations.add(location)
            else:
                scenario_has_undefined_steps = False
                with open(os.path.join(self.cached_steps_dir, tag), 'w') as f:
                    tag_steps_locations_str = json.dumps(sorted(scenario_step_locations))
                    f.write(tag_steps_locations_str)

            if scenario_has_undefined_steps:
                tests_logger.warning(f'Scenario {tag} has undefined steps.')


class ParallelBehaveRunner(BehaveRunner):
    """Раннер для параллельного запуска тестов.

    """
    parallel_features_scenarios = None

    def __init__(self, config, **kwargs):
        self.features_steps_definitions_dirs = {}
        super().__init__(config, **kwargs)

    def should_run_feature(self, feature):
        """
        Проверка наличия сценариев для тестирования
        """
        return self.parallel_features_scenarios[hash(feature)]

    def pre_run_feature(self, feature):
        """Действия перед запуском feature"""
        if self.features_steps_definitions_dirs:
            self.load_step_definitions(feature=feature)

    def get_step_locations(self, feature=None) -> set:
        """
        Получить пути до директорий steps. Если есть закэшированные пути, использовать их.
        """
        feature_definitions = None
        step_locations = set()

        if feature and self.features_steps_definitions_dirs:
            try:
                feature_definitions = self.features_steps_definitions_dirs[feature.filename]
            except KeyError:
                # Если feature новая, или по какой-то причине не оказалось в файле,
                # попробуем найти путь по feature-файлу.
                step_locations.add(
                    os.path.join(os.path.dirname(feature.filename), self.config.steps_dir)
                )

            if feature_definitions:
                try:
                    for sc_hash in self.parallel_features_scenarios[hash(feature)]:
                        step_locations.update(feature_definitions[sc_hash])
                except KeyError as e:
                    tests_logger.warning(
                        f'Ошибка при получении путей к step_definitions сценария из '
                        f'{os.path.basename(feature.filename)}: {e}'
                    )
                    # добавим все пути относящиеся к feature
                    step_locations.update(itertools.chain(*feature_definitions.values()))
                    step_locations.add(
                        os.path.join(os.path.dirname(feature.filename), self.config.steps_dir)
                    )

        else:
            step_locations = super().get_step_locations(feature=feature)

        return step_locations

    def parallel_run_model(self, features=None, tags=None, results_list=None, **kwargs):
        """Запуск run_model в отдельном потоке и сбор результатов в results_list.

        Args:
            features: Список объектов Feature.
            tags: Список тэгов.
            results_list: Список хранения результатов выполнения потоков.
        """
        # Поиск группового тэга и запись его номера в group_number.
        group_tag = [tag for tag in tags if scenario_group_prefix in tag][0]
        self.config.group_number = group_tag.replace(scenario_group_prefix, '')

        # Изменим порядок следования feature для отдельного потока
        random.shuffle(features)

        failed = self.run_model(features)

        results_list.append(failed)

    def run_with_paths(self):
        """Переопределен для возможности запуска в несколько потоков.

        """
        self.context = Context(self)
        self.load_hooks(filename=self.environment_filepath)

        if self.config.optimize_features_steps_loading:
            try:
                with open(self.config.optimize_features_steps_loading) as f:
                    self.features_steps_definitions_dirs = {
                        feature: {
                            hash(step): set(definitions)
                            for step, definitions in scenarios.items()
                        }
                        for feature, scenarios in json.loads(f.read()).items()
                    }
            except Exception as e:
                tests_logger.warning(
                    f"Ошибка при попытке открыть файл {self.config.optimize_features_steps_loading}: {e}"
                )

        if not self.features_steps_definitions_dirs:
            self.load_step_definitions()

        feature_locations = self.get_filtered_feature_locations()
        features = parse_features(feature_locations, language=self.config.lang)
        self.features.extend(features)

        failed = self.run_parallel_processes()

        self.do_after_parallel_run()

        return failed

    def prepare_process_kwargs(self, manager):
        """Создаёт словарь именованных аргументов для отдельного процесса.
        В случае если у репортера определён атрибут process_kwarg_name, инициализируем переменную и добавляем в словарь.

        Args:
            manager: объект multiprocessing.Manager
        """
        data = {}

        for reporter in self.config.reporters:
            if hasattr(reporter, 'process_kwarg_name'):
                data[reporter.process_kwarg_name] = reporter.init_process_variable(manager)

        return data

    def do_after_parallel_run(self):
        """Вызывает метод after_parallel_run для каждого репортера у которого есть соответствующий метод.
        """
        for reporter in self.config.reporters:
            if hasattr(reporter, 'after_parallel_run'):
                reporter.after_parallel_run()

    def prepare_parallel_feature_scenarios_map(self, manager, features):
        """Подготовить DictProxy карту сценариев по указанным feature-файлам.

        Args:
            manager: объект multiprocessing.Manager
            features: список объектов Feature

        Returns:
            DictProxy с ключами feature и значениями ListProxy --
             списком идентификаторов сценариев которые нужно выполнить.
        """
        self.parallel_features_scenarios = manager.dict()

        for feature in features:
            sc_keys = list(feature.scenarios_map.keys())
            random.shuffle(sc_keys)

            self.parallel_features_scenarios[hash(feature)] = manager.list(sc_keys)

        return self.parallel_features_scenarios

    def run_parallel_processes(self):
        """Запуск тестов в параллельных процессах.

        """
        groups, used_features = self.prepare_groups_and_features(
            self.config.parallel_count,
        )

        manager = multiprocessing.Manager()
        failed_results_list = manager.list()

        process_kwargs = self.prepare_process_kwargs(manager)
        process_kwargs['parallel_features_scenarios'] = self.prepare_parallel_feature_scenarios_map(
            manager,
            used_features,
        )

        jobs = []

        for group_tag in groups:
            process = multiprocessing.Process(
                target=self.parallel_run_model,
                args=(
                    used_features,
                    [group_tag],
                    failed_results_list,
                ),
                kwargs=process_kwargs,
            )
            jobs.append(process)

        start_time = datetime.datetime.now()

        for j in jobs:
            j.start()

        for j in jobs:
            j.join()

        if self.config.junit:
            self.combine_junit_reports(start_time)

        # Если хотя бы один результат True - значит было падение тестов
        return any(failed_results_list)

    def prepare_groups_and_features(self, groups_count=1):
        """Формирует группы, в зависимости от количества сценариев и указанного числа групп.
        Так же формирует список feature-файлов которые будут запускаться в зависимости от тегов.

        Args:
            groups_count: Количество групп.

        Returns:
            Список тегов групп, список объектов Feature
        """
        used_features = set()
        groups = []
        scenarios_count = 0

        for feature in self.features:
            if 'skip' in feature.tags:
                continue

            # сформируем карту соответствия идентификатора сценария и объекта сценария
            feature.scenarios_map = {}

            for sc in feature:
                if sc.should_run_with_tags(self.config.tags):
                    used_features.add(sc.feature)

                    if sc.type == 'scenario_outline':
                        for sub_sc in sc.scenarios:
                            feature.scenarios_map[hash(f'{sub_sc.name}{sub_sc.location}')] = sub_sc
                    else:
                        feature.scenarios_map[hash(f'{sc.name}{sc.location}')] = sc

            scenarios_count += len(feature.scenarios_map.keys())

        limit = (
            groups_count
            if scenarios_count > groups_count else
            scenarios_count
        )

        for i in range(limit):
            # фиктивный тег для группы
            group_tag = f'{scenario_group_prefix}{i}'
            groups.append(group_tag)

        return groups, list(used_features)

    def combine_junit_reports(self, start_time):
        """Объединяет части junit-отчётов полученные при выполнении параллельных процессов.

        Args:
            start_time: Время запуска процессов.

        """
        reports_combiner = JunitReportsCombiner(
            tests_execution_start_time=start_time,
            reports_dir_path=self.config.junit_directory,
            rerun=getattr(self.config, 'rerun', False),
        )
        reports_combiner.join_reports()

        if self.config.collect_top_scenarios:
            reports_combiner.export_top_scenarios_by_time()
