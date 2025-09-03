import io
from typing import (
    Any,
    Dict,
)

from django.http.response import (
    HttpResponse,
)

from behave_bo.enums import (
    StepTypeEnum,
)
from behave_bo.behave_django_bo.signals import (
    skip_request_check_signal,
)


class AppRequest:
    """
    Запрос к приложению
    """

    def __init__(
        self,
        path: str,
        method: str,
        context,
        parameters: Dict[str, Any],
        force: bool = False,
    ):
        self._path = path
        self._method = method
        self._context = context
        self._parameters = parameters
        self._force = force

    def execute(self) -> HttpResponse:
        """
        Выполнение запроса к приложению
        """
        method = getattr(self._context.session, self._method.lower())

        skip_request = self.check_skip_request()

        if self._force or not skip_request:
            response = method(
                path=self._path,
                data=self._parameters
            )
            is_used = True
        else:
            response = HttpResponse()
            is_used = False

        if self._context.config.remove_readonly_requests:
            self._context.config.django_test_runner.collect_requests_data(is_used)

        for parameter in self._parameters.values():
            if isinstance(parameter, io.IOBase):
                parameter.close()
            elif isinstance(parameter, list):
                for item in parameter:
                    if isinstance(item, io.IOBase):
                        item.close()

        return response

    def check_skip_request(self) -> bool:
        """
        Проверка параметра пропуска запроса
        """
        skip_request = False

        if (
            (self._context.config.skip_readonly_requests or self._context.config.remove_readonly_requests)
            and hasattr(self._context, 'current_step') and self._context.current_step.step_type != StepTypeEnum.THEN
        ):
            if self._context.config.skip_readonly_requests_url_endings:
                skip_url_endings = self._context.config.skip_readonly_requests_url_endings.split(',')
            else:
                # TODO Указать адреса для списка ниже на уровне web-bb-core
                skip_url_endings = [
                    '/rows',
                    '/edit',
                    '/list',
                    '/select',
                    '/check_notify',
                ]

            if any(self._path.endswith(url) for url in skip_url_endings) and self.check_skip_request_signal():
                skip_request = True

        return skip_request

    def check_skip_request_signal(self):
        results = skip_request_check_signal.send(sender=self)
        return all(res for _, res in results)
