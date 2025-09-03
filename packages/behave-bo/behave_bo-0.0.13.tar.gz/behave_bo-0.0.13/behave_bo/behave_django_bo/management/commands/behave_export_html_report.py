from django.core.management.base import (
    BaseCommand,
)

from behave_bo.reporter.junit import (
    JunitReportsCombiner,
)


class Command(BaseCommand):
    help = "Обрабатывает junit xml-файлы, формирует общий html-отчёт выполнения автотестов."

    def add_arguments(self, parser):
        parser.add_argument('junit_directory', help='путь до директории xml-файлов отчётов junit', type=str)
        parser.add_argument('report_directory', help='директория в которой будет сформирован html-отчёт', type=str)

    def handle(self, *args, **options):
        reports_combiner = JunitReportsCombiner(
            reports_dir_path=options['junit_directory'],
            html_report_destination_path=options['report_directory'],
        )
        report_path = reports_combiner.export_html_report()
        self.stdout.write(
            self.style.SUCCESS(f'Html-отчёт результатов автотестов выгружен в файл {report_path}')
        )
