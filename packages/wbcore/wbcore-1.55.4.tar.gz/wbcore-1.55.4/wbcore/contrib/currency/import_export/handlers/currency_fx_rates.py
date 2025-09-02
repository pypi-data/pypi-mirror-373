from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from django.db import models

from wbcore.contrib.io.imports import ImportExportHandler

from .currency import CurrencyImportHandler


class CurrencyFXRatesImportHandler(ImportExportHandler):
    MODEL_APP_LABEL: str = "currency.CurrencyFXRates"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.currency_handler = CurrencyImportHandler(self.import_source)

    def _deserialize(self, data: Dict[str, Any]):
        data["date"] = datetime.strptime(data["date"], "%Y-%m-%d").date()
        data["currency"] = self.currency_handler.process_object(data["currency"])[0]
        data["value"] = round(Decimal(data["value"]), 6)

    def _get_instance(self, data: Dict[str, Any], history: Optional[models.QuerySet] = None, **kwargs) -> models.Model:
        return self.model.objects.filter(currency=data["currency"], date=data["date"]).first()

    def _create_instance(self, data: Dict[str, Any], **kwargs) -> models.Model:
        self.import_source.log += "\nCreate Fx Rate."
        return self.model.objects.create(**data, import_source=self.import_source)
