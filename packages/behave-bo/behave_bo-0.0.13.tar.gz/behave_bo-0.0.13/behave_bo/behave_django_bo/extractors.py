import json
import re


class ContextExtractor:
    """
    Утилита для преобразования контекста тестирования, ui-компонента или
    содержимого ответа на запрос в нужный для автотестов вид.
    """
    regex_patterns = []

    def extract_flat_dict_from_component(self, component, is_child_item=False, data=None):
        """Преобразовывает Ext-контейнер/поле в плоский словарь с ключами-значениями из вложенных полей.

        Args:
            component: Объект Ext-контейнера/поля.
            is_child_item: Признак вызова для дочернего компонента (в рекурсии).
            data: Словарь пробрасываемый при рекурсивном вызове.
        Returns:
            Плоский словарь содержащий значения полей.
        """
        if not data:
            data = {}

        return data

    def prepare_component_json(self, component):
        """Преобразует компонент в словарь и затем в json-строку.

        Args:
            component: Объект Ext-компонента.

        Returns:
            JSON-строка.
        """
        return json.dumps(
            self.extract_flat_dict_from_component(component),
            default=str,
        )

    def extract_data_with_regex(self, response_content) -> dict:
        """Извлекает из js-ответа данные с помощью регулярных выражений.

        Args:
            response_content: Контент ответа на запрос

        Returns:
            Словарь с результатами поиска.
        """
        response_content = response_content.decode()
        result = {}

        # В текущей реализации порядок добавления re паттернов имеет значение.
        for pattern in self.regex_patterns:
            result = pattern.search(response_content)
            if result:
                result = result.groupdict()
                for key, value in result.items():
                    try:
                        result[key] = json.loads(value)
                    except ValueError:
                        pass
                break

        return result

    def parse_download_file_name(self, content, download_url) -> str:
        """Парсит наименование скачиваемого файла.

        Args:
            content: Контент ответа на запрос.
            download_url: Путь скачивания файла

        Returns:
            Наименование файла.

        Raises:
            Exception: если параметры файла не найдены
        """
        match = re.findall(
            rf"(?<={download_url}).*?(?=\'|\"|$)",
            content
        )

        if match:
            file_name = match[0]
            if bool(re.search('[\\\\u]', file_name)):
                file_name = file_name.encode().decode('unicode-escape')
        else:
            raise Exception('Имя файла не найдено')

        return file_name
