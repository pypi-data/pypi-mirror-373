import json
from typing import Any

from wbcore.contrib.io.models import ImportSource

DUPLICATIONS_MAP = {"GBP": {"currency_key": "GBX", "factor": 100}}


def parse(import_source: ImportSource) -> dict[str, Any]:
    content = json.load(import_source.file)
    data = []
    for row in content:
        if row["success"]:
            val_date = row["date"]
            for currency_key, value in row["rates"].items():
                if duplicated_currency_data := DUPLICATIONS_MAP.get(currency_key, None):
                    data.append(
                        {
                            "currency__provider_id": duplicated_currency_data["currency_key"],
                            "currency__key": duplicated_currency_data["currency_key"],
                            "value": value * duplicated_currency_data["factor"],
                            "date": val_date,
                        }
                    )
                data.append(
                    {
                        "currency__provider_id": currency_key,
                        "currency__key": currency_key,
                        "value": value,
                        "date": val_date,
                    }
                )

    return {"data": data}
