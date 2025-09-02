from typing import Any, Dict

from django.db import models

from wbcore.contrib.io.imports import ImportExportHandler


class CurrencyImportHandler(ImportExportHandler):
    MODEL_APP_LABEL: str = "currency.Currency"

    def _deserialize(self, data: Dict[str, Any]):
        if key := data.get("key"):
            if key == "CNH":  # We switch CNH to CNY because we don't support it
                data["key"] = "CNY"
            if key == "GBp":
                data["key"] = "GBX"

    def _get_instance(self, data: Dict[str, Any], **kwargs) -> models.Model | None:
        try:
            if key := data.get("key", None):
                return self.model.objects.get(key=key)
            if _id := data.get("id", None):
                return self.model.objects.get(id=_id)
        except self.model.DoesNotExist:
            pass
