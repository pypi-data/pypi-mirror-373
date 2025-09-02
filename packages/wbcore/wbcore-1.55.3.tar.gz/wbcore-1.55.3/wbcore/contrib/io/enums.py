from django.db.models import IntegerChoices
from import_export.admin import ImportExportMixin


class ExportFormat(IntegerChoices):
    CSV = 0, "CSV"
    XLSX = 1, "XLSX"
    TSV = 2, "TSV"
    JSON = 3, "JSON"
    YAML = 4, "YAML"


def get_django_import_export_format(format: int):
    format_map = {f.__name__: f for f in ImportExportMixin().get_export_formats()}
    return format_map[ExportFormat(format).name]
