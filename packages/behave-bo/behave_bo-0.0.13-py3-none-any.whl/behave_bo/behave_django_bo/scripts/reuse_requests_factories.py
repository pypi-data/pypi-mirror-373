import argparse
import ast
import os
import re
import uuid
from collections import (
    defaultdict,
)
from pathlib import (
    Path,
)


class Storage:
    def __init__(self, processor_ins):
        self._processor_ins = processor_ins
        self.storage = defaultdict(dict)

    @property
    def project(self):
        return self._processor_ins.project_dir

    @property
    def records_in_project(self):
        return self.storage[self.project]

    def get(self, key):
        return self.records_in_project[key]


class FactoriesReuseProcessor:

    def __init__(self, base_path) -> None:
        self.base_path = base_path
        self.project_dir = ''

        self.factories_records = Storage(self)
        self.factories_imports = Storage(self)
        self.all_func_names = set()
        self.records_file_paths_for_factories = Storage(self)
        self.errors = []

        self.collect_factories_data()

    def _set_project_dir(self, absolute_path: str):
        self.project_dir = absolute_path.replace(f'{self.base_path}/', '').split('/')[0].replace('-', '_')

    def _get_project_dir_by_factory_name(self, factory_name):
        """Определяет директорию проекта, к которой относится фабрика"""

        # Фабрика с наименованием ActualReportStorageFactory есть и в core и в salary, при этом фабрика из salary
        # используется только в старых реализациях, соответственно используем только из core.
        excluded_factories = {
            'ActualReportStorageFactory',
        }

        if (
            factory_name not in excluded_factories and
            factory_name in self.records_file_paths_for_factories.records_in_project
        ):
            project_dir = self.project_dir
        else:
            if (
                self.project_dir in ('web_bb_vehicle', 'web_bb_food') and
                factory_name in self.records_file_paths_for_factories.storage['web_bb_accounting']
            ):
                project_dir = 'web_bb_accounting'
            else:
                project_dir = 'web_bb_core'

        return project_dir

    def collect_factories_records_data(self, records_filepath):
        with open(records_filepath) as f:
            ast_tree = ast.parse(f.read())

        for item in ast_tree.body:
            if isinstance(item, ast.FunctionDef):
                class_call = item.body[0].value
                corrected_keywords = set()

                for k in class_call.keywords:
                    if 'kwargs[' in ast.unparse(k.value):
                        unparsed_val = f"{k.value.value.slice.value}.pk"  # ".pk" очень важно!
                    else:
                        unparsed_val = ast.unparse(k.value)

                    corrected_keywords.add((k.arg, unparsed_val))

                key_id = frozenset(corrected_keywords)

                func_name = item.name

                self.all_func_names.add(func_name)

                factory_name = class_call.func.id

                try:
                    self.factories_records.records_in_project[factory_name][key_id] = (func_name, False)
                except KeyError:
                    self.factories_records.records_in_project[factory_name] = {key_id: (func_name, False)}

    def collect_factories_data(self):
        for dir_name, sub_dirs, file_list in os.walk(self.base_path):
            self._set_project_dir(dir_name)
            if 'pycache' in dir_name:
                continue
            elif 'features/factories' in dir_name:
                for f_name in file_list:
                    if '__init__.py' in f_name:
                        continue
                    elif f_name == 'records.py':
                        self.collect_factories_records_data(f'{dir_name}/{f_name}')
                    else:
                        with open(f'{dir_name}/{f_name}') as f:
                            ast_tree = ast.parse(f.read())

                        for item in ast_tree.body:
                            if isinstance(item, ast.ClassDef):
                                self.records_file_paths_for_factories.records_in_project[item.name] = f'{dir_name}/records.py'

    def process_ast_imports(self, ast_tree, app_request_strs):

        def exclusion_required(string):
            """Условие удаление импорта."""

            return (
                ('datetime.' not in app_request_strs and 'import datetime' in string) or
                'AppRequest,' in string or
                'Decimal,' in string or
                'ReportType,' in string
            )

        new_import_lines = []

        for item in ast_tree.body:
            if isinstance(item, ast.Import):
                new_import_lines.append(f'{ast.unparse(item)}\n')
            elif isinstance(item, ast.ImportFrom):
                if 'features.factories.records' in item.module:
                    new_import_lines.append(f'{ast.unparse(item)}\n')
                elif 'features.factories' in item.module:
                    import_module = item.module.split('features.factories')[0]
                    new_import_lines.append(f'from {import_module}features.factories.records import *\n')
                    for name_obj in item.names:
                        factory_name = name_obj.name
                        project_dir = self._get_project_dir_by_factory_name(factory_name)
                        self.factories_imports.storage[project_dir][factory_name] = item.module
                else:
                    import_names = ''.join(f'    {n.name},\n' for n in item.names)
                    new_import_lines.append(
                        f'from {item.module} import (\n{import_names})\n'
                    )

        return [i for i in new_import_lines if not exclusion_required(i)]

    def process_factories(self, ast_tree):
        new_function_strs = []

        for item in ast_tree.body:
            if isinstance(item, (ast.Import, ast.ImportFrom)):
                continue
            elif isinstance(item, ast.FunctionDef):
                if item.name == 'request_loader':
                    new_function_strs.append(f'\n\ndef {item.name}({ast.unparse(item.args)}):\n')
                    for el in item.body:
                        if re.search(r'.*Factory(___[\d\w]+)?\(', ast.unparse(el)):
                            factory_func_name = None
                            line_variables = ''

                            if isinstance(el, ast.Assign) or isinstance(el, ast.Expr):
                                variable_name = None

                                if isinstance(el, ast.Assign):
                                    line_variables = ' = '.join([t.id for t in el.targets])
                                    line_variables = f'{line_variables} = '
                                    variable_name = el.targets[0].id

                                    line_variables = re.sub(r'___[a-z\d]+', '', line_variables)
                                    variable_name = re.sub(r'___[a-z\d]+', '', variable_name)

                                keywords = set()
                                for k in el.value.keywords:
                                    keyword_value = ast.unparse(k.value)
                                    if keyword_value.endswith('.pk') and '___' in keyword_value:
                                        keyword_value = re.sub(r'___[a-z\d]+', '', keyword_value)
                                    keywords.add((k.arg, keyword_value))

                                factory_func_name = self.get_factory_func_name(
                                    el.value.func.id,
                                    keywords,
                                    variable_name=variable_name,
                                )

                            if factory_func_name:
                                new_function_strs.append(f'    {line_variables}{factory_func_name}(**locals())\n')
                        elif 'AppRequest' in ast.unparse(el):
                            break
                        else:
                            new_function_strs.append(f'    {ast.unparse(el)}\n')

        return new_function_strs

    def get_factory_func_name(self, factory_name, keywords, variable_name=None):
        new_func_name = "???!"

        factory_name, *_ = factory_name.split('___')
        project_dir = self._get_project_dir_by_factory_name(factory_name)

        key_id = frozenset(keywords)
        try:
            # exists_func_name, is_new = self.factories_records[factory_name].get(key_id, (None, False))
            exists_func_name, is_new = self.factories_records.storage[project_dir][factory_name].get(key_id, (None, False))
        except KeyError:
            exists_func_name = None
            # self.factories_records[factory_name] = {}
            self.factories_records.storage[project_dir][factory_name] = {}

        if not exists_func_name:
            if variable_name:
                new_func_name = f'get_{variable_name}'
            else:
                new_func_name = f'get_{factory_name.lower()}_{uuid.uuid4().hex[:6]}'

            if new_func_name in self.all_func_names:
                new_func_name = f'{new_func_name}_{uuid.uuid4().hex[:6]}'

            self.all_func_names.add(new_func_name)
            self.factories_records.storage[project_dir][factory_name][key_id] = (new_func_name, True)

        if exists_func_name:
            factory_func_name = exists_func_name
        else:
            factory_func_name = new_func_name

        return factory_func_name

    def process_file(self, file_path):
        if not ('/request_' in str(file_path) and str(file_path).endswith('.py')):
            return

        print(f'process {file_path}')

        new_file_lines = []

        with open(file_path) as f:
            content = f.read()

        if '.records import *' in content:
            print('already processed!')
            return

        ast_tree = ast.parse(content)
        _, response_param_name, _, app_request_strs = re.split(
            r'(response.*) = (context\.AppRequest|AppRequest)',
            content,
            maxsplit=1,
        )

        new_file_lines.append(
            ''.join(
                self.process_ast_imports(ast_tree, app_request_strs) +
                self.process_factories(ast_tree) +
                [f'\n    {response_param_name} = context.AppRequest{app_request_strs}']
            )
        )

        with open(file_path, 'w') as f:
            f.write(f'{"".join(new_file_lines).strip()}\n')

    def make_requests_factories_reuse(self, path):
        """
        """
        for path in path.split(','):
            self._set_project_dir(path)
            path = Path(path)

            if path.is_dir():
                for dir_name, sub_dirs, file_list in os.walk(path):
                    if 'pycache' in dir_name:
                        continue
                    if 'features/' in dir_name:
                        for file_name in file_list:
                            try:
                                self.process_file(f'{dir_name}/{file_name}')
                            except Exception as e:
                                self.errors.append((f'{dir_name}/{file_name}', str(e)))

            elif path.is_file():
                try:
                    self.process_file(path)
                except Exception as e:
                    self.errors.append((path, str(e)))

        self.update_factories_records()

        if self.errors:
            print('=' * 100)
            for path, err in self.errors:
                print(f'{path} - {err}')

    def update_factories_records(self):
        print('update_factories_records:')
        files_to_update = defaultdict(list)

        for project_dir, factories_records in self.factories_records.storage.items():
            for factory_name, records_data in factories_records.items():
                for keywords, (func_name, is_new) in records_data.items():
                    if is_new:
                        files_to_update[self.records_file_paths_for_factories.storage[project_dir][factory_name]].append(
                            (func_name, factory_name, keywords)
                        )

        for file_path, factory_functions in files_to_update.items():
            import_decimal = False
            import_datetime = False

            file_lines = []
            factory_import_lines = set()

            for func_name, factory_name, keywords in factory_functions:
                sorted_keywords = []

                for k, v in sorted(keywords):
                    if v.endswith('.pk'):
                        kwarg_var = v.split('.')[0]
                        v = f'kwargs[\'{kwarg_var}\'].pk'
                    elif 'Decimal' in v:
                        import_decimal = True
                    elif 'datetime' in v:
                        import_datetime = True

                    sorted_keywords.append(f'        {k}={v},')

                sorted_keywords = '\n'.join(sorted_keywords)
                file_lines.append(
                    f'def {func_name}(**kwargs):\n'
                    f'    return {factory_name}(\n'
                    f'{sorted_keywords}\n'
                    f'    )\n\n'
                )
                # self.factories_records[factory_name][keywords] = (func_name, False)
                project_dir = self._get_project_dir_by_factory_name(factory_name)
                self.factories_records.storage[project_dir][factory_name][keywords] = (func_name, False)
                factory_import_lines.add(f'from {self.factories_imports.storage[project_dir][factory_name]} import *')

            imports_lines = []

            if os.path.isfile(file_path):
                print(f'\tupdate: {file_path}')

                with open(file_path, 'r+') as f:
                    exists_file_content = f.read()

                    if import_decimal and 'Decimal' not in exists_file_content:
                        imports_lines.append('from decimal import Decimal')
                    if import_datetime and 'datetime' not in exists_file_content:
                        imports_lines.append('import datetime')

                    f.seek(0)
                    f.write('\n'.join(
                        imports_lines + [exists_file_content, ''] + file_lines
                    ))
                    f.truncate()
            else:
                print(f'\tcreate: {file_path}')

                if import_decimal and 'Decimal':
                    imports_lines.append('from decimal import Decimal')
                if import_datetime and 'datetime':
                    imports_lines.append('import datetime')

                imports_lines.extend(list(factory_import_lines) + ['\n'])

                with open(file_path, 'w+') as f:
                    f.write('\n'.join(
                        imports_lines + file_lines
                    ))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Перенос и объединение кода получения фабрик.')

    parser.add_argument('base_path', help='Базовая директория расположения web_bb репозиториев', type=str)
    parser.add_argument('path', help='Путь к файлу или директории для которой нужно выполнить обработку', type=str)

    args = parser.parse_args()

    reuse_proc = FactoriesReuseProcessor(args.base_path)
    reuse_proc.make_requests_factories_reuse(args.path)
