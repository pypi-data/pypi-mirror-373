import sys

from behave_bo import (
    __version__,
)
from behave_bo.configuration import (
    ConfigError,
    Configuration,
)
from behave_bo.parser import (
    ParserError,
)
from behave_bo.runner import (
    Runner,
)
from behave_bo.runner_util import (
    FileNotFoundError,
    InvalidFileLocationError,
    InvalidFilenameError,
    print_undefined_step_snippets,
    reset_runtime,
)
from behave_bo.textutil import (
    compute_words_maxsize,
    text as _text,
)


TAG_HELP = """
Scenarios inherit tags declared on the Feature level. The simplest
TAG_EXPRESSION is simply a tag::

    --tags @dev

You may even leave off the "@" - behave_bo doesn't mind.

When a tag in a tag expression starts with a ~, this represents boolean NOT::

    --tags ~@dev

A tag expression can have several tags separated by a comma, which represents
logical OR::

    --tags @dev,@wip

The --tags option can be specified several times, and this represents logical
AND, for instance this represents the boolean expression
"(@foo or not @bar) and @zap"::

    --tags @foo,~@bar --tags @zap.

Beware that if you want to use several negative tags to exclude several tags
you have to use logical AND::

    --tags ~@fixme --tags ~@buggy.
""".strip()


def run_behave(config, runner_class=None, runner_kwargs=None):
    """Run behave_bo with configuration.

    :param config:          Configuration object for behave_bo.
    :param runner_class:    Runner class to use or none (use Runner class).
    :param runner_kwargs:   Runner class init kwargs
    :return:    0, if successful. Non-zero on failure.

    .. note:: BEST EFFORT, not intended for multi-threaded usage.
    """
    # pylint: disable=too-many-branches, too-many-statements, too-many-return-statements
    if runner_class is None:
        runner_class = Runner

    if runner_kwargs is None:
        runner_kwargs = {}

    if config.version:
        print("behave " + __version__)
        return 0

    if config.tags_help:
        print(TAG_HELP)
        return 0

    if config.lang_list:
        from behave_bo.i18n import (
            languages,
        )
        stdout = sys.stdout
        iso_codes = languages.keys()
        print("Languages available:")
        for iso_code in sorted(iso_codes):
            native = languages[iso_code]["native"][0]
            name = languages[iso_code]["name"][0]
            print(f"{iso_code}: {native} / {name}", file=stdout)
        return 0

    if config.lang_help:
        from behave_bo.i18n import (
            languages,
        )
        if config.lang_help not in languages:
            print("%s is not a recognised language: try --lang-list" % \
                  config.lang_help)
            return 1
        trans = languages[config.lang_help]
        print("Translations for {} / {}".format(trans["name"][0],
                                                trans["native"][0]))
        for kw in trans:
            if kw in "name native".split():
                continue
            print("%16s: %s" % (kw.title().replace("_", " "),
                                ", ".join(w for w in trans[kw] if w != "*")))
        return 0

    if not config.format:
        config.format = [config.default_format]
    elif config.format and "format" in config.defaults:
        # -- CASE: Formatter are specified in behave_bo configuration file.
        #    Check if formatter are provided on command-line, too.
        if len(config.format) == len(config.defaults["format"]):
            # -- NO FORMATTER on command-line: Add default formatter.
            config.format.append(config.default_format)
    if "help" in config.format:
        print_formatters("Available formatters:")
        return 0

    if len(config.outputs) > len(config.format):
        print("CONFIG-ERROR: More outfiles (%d) than formatters (%d)." % \
              (len(config.outputs), len(config.format)))
        return 1

    # -- MAIN PART:
    failed = True
    try:
        reset_runtime()
        runner = runner_class(config, **runner_kwargs)
        failed = runner.run()
    except ParserError as e:
        print("ParserError: %s" % e)
    except ConfigError as e:
        print("ConfigError: %s" % e)
    except FileNotFoundError as e:
        print("FileNotFoundError: %s" % e)
    except InvalidFileLocationError as e:
        print("InvalidFileLocationError: %s" % e)
    except InvalidFilenameError as e:
        print("InvalidFilenameError: %s" % e)
    except Exception as e:
        # -- DIAGNOSTICS:
        text = _text(e)
        print(f"Exception {e.__class__.__name__}: {text}")
        raise

    if config.show_snippets and runner.undefined_steps:
        print_undefined_step_snippets(runner.undefined_steps,
                                      colored=config.color)

    return_code = 0
    if failed:
        return_code = 1
    return return_code


def print_formatters(title=None, stream=None):
    """Prints the list of available formatters and their description.

    :param title:   Optional title (as string).
    :param stream:  Optional, output stream to use (default: sys.stdout).
    """
    from operator import (
        itemgetter,
    )

    from behave_bo.formatter._registry import (
        format_items,
    )

    if stream is None:
        stream = sys.stdout
    if title:
        stream.write("%s\n" % title)

    format_items = sorted(format_items(resolved=True), key=itemgetter(0))
    format_names = [item[0] for item in format_items]
    column_size = compute_words_maxsize(format_names)
    schema = "  %-" + _text(column_size) + "s  %s\n"
    for name, formatter_class in format_items:
        formatter_description = getattr(formatter_class, "description", "")
        stream.write(schema % (name, formatter_description))


def main(args=None):
    """Main function to run behave_bo (as program).

    :param args:    Command-line args (or string) to use.
    :return: 0, if successful. Non-zero, in case of errors/failures.
    """
    config = Configuration(args)
    return run_behave(config)


if __name__ == "__main__":
    # -- EXAMPLE: main("--version")
    sys.exit(main())
