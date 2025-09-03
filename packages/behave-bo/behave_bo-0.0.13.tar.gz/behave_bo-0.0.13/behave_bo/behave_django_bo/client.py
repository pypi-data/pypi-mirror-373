import inspect
import traceback

from django.test.client import (
    Client,
)

from behave_bo.loggers import (
    tests_logger,
)


class BehaveBOClient(Client):

    def __init__(self):
        super().__init__()
        self.non_200_requests = list()
        self.code_parts = ['AppRequest(', '.get_raw_data(']

    def find_code_context(self):
        stack = inspect.stack()
        file_name = None
        break_flag = False
        for frame in stack:
            for code in frame.code_context:
                if any(part in code for part in self.code_parts):
                    file_name = f"{frame.filename}:{frame.lineno}"
                    break_flag = True
                    break
            if break_flag:
                break

        if file_name is None:
            for line in traceback.format_stack():
                print(line.strip())

        return file_name

    def request(self, **request):
        response = super().request(**request)

        if response.status_code != 200:
            file_name = self.find_code_context()
            self.non_200_requests.append((file_name, response.request["PATH_INFO"], response.status_code))

        return response

    def print_non_200_requests(self) -> None:
        """Выводит в консоль список запросов, которые завершились с ошибкой"""
        if self.non_200_requests:
            tests_logger.error('Список запросов к приложению, завершившихся с ошибкой:')
            for file_name, request_path, status_code in self.non_200_requests:
                tests_logger.error(f'{file_name} - {request_path} - {status_code}')
        self.non_200_requests = list()
