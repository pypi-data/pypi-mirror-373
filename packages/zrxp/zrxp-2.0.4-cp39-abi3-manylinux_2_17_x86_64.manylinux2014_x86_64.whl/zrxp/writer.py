from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any, Union

import pandas as pd
import polars as pl
from pydantic import BaseModel

from .data import ZRXPMetadata, model_dump, model_validate, parse_timezone

# TODO: What if no values?; whitespace in layout keys

# def write_rust(
#         data: list[pd.DataFrame | pl.DataFrame],
#         metadata: list[dict[str, Any]],
#         file: str
# ):
#     assert len(data) == len(metadata), "Length of Data and Metadata not equivalent"
#     _write_zrxp(
#         [d.with_columns(
#             pl.col(c).cast(pl.Utf8) for c in d.columns
#         ).to_dict(as_series=False) for d in data],
#         [{k: str(v)} for m in metadata for k, v in m.items()],
#         file
#     )


FIRST_COLUMNS = ["timestamp", "value", "status", "interpolation_type"]
STATUS_COLUMN_NAMES = {"quality", "value.status", "value.quality"}
INTERPOLATION_COLUMN_NAMES = {"value.interpolation", "interpolation"}
DataFrameType = Union[pd.DataFrame, pl.DataFrame]
MetadataType = Union[dict[str, Any], ZRXPMetadata, BaseModel]


def _write(
    data: DataFrameType | list[DataFrameType],
    metadata: MetadataType | list[MetadataType],
) -> BytesIO:
    if isinstance(data, (pd.DataFrame, pl.DataFrame)):
        data = [data]
    if isinstance(metadata, (dict, BaseModel)):
        metadata = [metadata]
    if len(data) != len(metadata):
        raise ValueError(f"Length of data ({len(data)}) and metadata ({len(metadata)}) not equivalent")
    stream = BytesIO()
    for d, m in zip(data, metadata):
        if isinstance(d, pd.DataFrame):
            d.index = d.index.rename("timestamp")
            d = pl.from_pandas(d, include_index=True)

        m = model_dump(model_validate(ZRXPMetadata, m), exclude_none=True)
        stream.write("".join([f"#{key}{value}|*|\n" for key, value in m.items()]).encode())

        # sort layout as timestamp->value->status->interpolation_type->others
        columns = list(d.columns)
        for i, col in enumerate(columns):
            if col.lower() in STATUS_COLUMN_NAMES:
                columns[i] = "status"
                d.rename({col: "status"})
            if col.lower() in INTERPOLATION_COLUMN_NAMES:
                columns[i] = "interpolation_type"
                d.rename({col: "interpolation_type"})
        layout = [col for col in FIRST_COLUMNS if col in columns] + [
            col for col in columns if col not in FIRST_COLUMNS
        ]
        stream.write(f"#LAYOUT({','.join(layout)})\n".encode())

        meta_tz = parse_timezone(m.get("TZ", "UTC"))
        if d["timestamp"].dtype.time_zone and d["timestamp"].dtype.time_zone != meta_tz:  # type: ignore
            d = d.with_columns(d["timestamp"].dt.convert_time_zone(meta_tz))
        invalid_value = float(m.get("RINVAL", -777))
        if "value" in layout:
            d = d.with_columns(d["value"].fill_null(value=invalid_value).fill_nan(value=invalid_value))
        if "status" in layout:
            default_quality = int(m.get("DEFQUALITY", 200))
            d = d.with_columns(d["status"].fill_null(value=default_quality))
        d.select(layout).write_csv(
            stream, include_header=False, separator=" ", datetime_format="%Y%m%d%H%M%S"
        )

    return stream


def write(
    filename: str | Path,
    data: DataFrameType | list[DataFrameType],
    metadata: MetadataType | list[MetadataType],
) -> None:
    """
    Write Data to a ZRXP file

    :param filename: File to write the data to
    :param data: List of DataFrames containing the data
    :param metadata: List of Dictionaries containing the metadata
                    associated with each DataFrame
    :return: None
    """
    zrxp = _write(data, metadata)
    with open(filename, "wb") as f:
        f.write(zrxp.getbuffer())


def writes(
    data: DataFrameType | list[DataFrameType],
    metadata: MetadataType | list[MetadataType],
) -> str:
    """
    Write Data and Metadata to a ZRXP string

    :param data: List of DataFrames containing the data
    :param metadata: List of Dictionaries containing the metadata
                    associated with each DataFrame
    :return: String representation of the zrxp file
    """
    zrxp = _write(data, metadata)
    zrxp.seek(0)
    return zrxp.read().decode()
