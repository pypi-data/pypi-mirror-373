import os
import traceback
from functools import (
    wraps,
)

from behave_bo.loggers import (
    tests_logger,
)
from coverage import (
    Coverage,
    CoverageException,
)


def coverage_switch_context(func):
    """
    Декоратор для переключения динамического контекста при анализе покрытия кода.
    Прокидывает в отчёт покрытия информацию о файле из которого был отправлен запрос.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):

        if self._context.config.measure_requests_coverage:
            coverage = Coverage.current()
            frame = traceback.extract_stack()[-2]  # фрейм с файлом и функцией отправки запроса
            basename = os.path.basename(frame.filename)

            try:
                if coverage:
                    tests_logger.info(f'switch context! {basename}')
                    coverage.switch_context(basename)
            except CoverageException as e:
                tests_logger.info(str(e))

        return func(self, *args, **kwargs)

    return wrapper
