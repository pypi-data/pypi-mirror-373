import csv
import re
from _csv import Error

import numpy as np
import pandas as pd


def parse(import_source):
    # try to guess the delimiter
    try:
        with import_source.file.open(mode="r") as file:
            sep = csv.Sniffer().sniff(file.readline()).delimiter
    except Error:
        sep = ","

    df = pd.read_csv(import_source.file, sep=sep)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]  # remove columns without names
    # in case we have import kwargs, we set them as column values
    columns_mapping = import_source.resource_kwargs.get("columns_mapping", {})
    extra_columns_values = import_source.resource_kwargs.get("extra_columns_values", {})
    for k, v in extra_columns_values.items():
        df[k] = v
    df = df.rename(columns=columns_mapping)
    df = df.replace([np.inf, -np.inf, np.nan], None)
    rows = []
    for row in df.convert_dtypes().to_dict(orient="records"):
        for k, v in row.items():
            if isinstance(v, str):
                # we remove any whitespace special characters
                row[k] = re.sub(r"\s+", "", v.strip())
        rows.append(row)
    data = {"data": rows}
    if extra_columns_values:
        data["history"] = extra_columns_values
    return data
