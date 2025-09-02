from import_export.widgets import ForeignKeyWidget

from wbcore.contrib.geography.models import Geography


class CountryForeignKeyWidget(ForeignKeyWidget):
    def __init__(self, field="code_3", use_natural_foreign_keys=False, **kwargs):
        super().__init__(Geography, field=field)

    def get_queryset(self, value, row, *args, **kwargs):
        return Geography.countries.all()
