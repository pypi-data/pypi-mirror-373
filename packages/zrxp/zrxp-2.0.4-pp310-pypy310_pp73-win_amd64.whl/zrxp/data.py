from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Optional, TypeVar, Union

import pandas as pd
import polars as pl
from pydantic import BaseModel, Field

from ._core import ZRXPData as _ZRXPData
from .exceptions import ZRXPReadError

BaseModelT = TypeVar("BaseModelT", bound=BaseModel)
try:
    from pydantic import ConfigDict, v1  # noqa: F401

    class MetadataBaseModel(BaseModel):
        model_config = ConfigDict(populate_by_name=True)

    def model_validate(model: type[BaseModelT] | BaseModelT, obj: Any) -> BaseModelT:
        return model.model_validate(obj)

    def model_dump(model: BaseModelT, **kwargs: Any) -> dict[str, Any]:
        return model.model_dump(**kwargs)
except ImportError:

    class MetadataBaseModel(BaseModel):  # type: ignore
        class Config:
            allow_population_by_alias = True

    def model_validate(model: type[BaseModelT] | BaseModelT, obj: Any) -> BaseModelT:
        return model.parse_obj(obj)

    def model_dump(model: BaseModelT, **kwargs: Any) -> dict[str, Any]:
        return model.dict(**kwargs)


DATATYPES = {
    "value": pl.Float32,
    "status": pl.UInt8,
    "translatedStatus": pl.Utf8,
    "primary_status": pl.UInt8,
    "interpolation_type": pl.Int16,
    "remark": pl.Utf8,
    "occurrencecount": pl.Int64,
    "member": pl.Utf8,
    "releaselevel": pl.Utf8,
    "dispatchinfo": pl.Utf8,
    "dispatch_info": pl.Utf8,
    "additional_status": pl.Utf8,
}

DATETIME_COLUMNS = {"timestamp", "timestampoccurrence", "forecast"}


class Engine(str, Enum):
    POLARS = "polars"
    PANDAS = "pandas"


def apply_engine(
    df: pl.DataFrame, engine: Engine | Literal["polars", "pandas"]
) -> pd.DataFrame | pl.DataFrame:
    if engine == Engine.PANDAS:
        return df.to_pandas().set_index("timestamp")
    else:
        return df


def convert_series(
    s: pl.Series, timezone: str = "UTC", invalid_value: float = -777, default_quality: int = 200
) -> pl.Series:
    if s.name in DATETIME_COLUMNS:
        s = s.str.to_datetime(format="%Y%m%d%H%M%S").dt.replace_time_zone(time_zone=timezone)
    else:
        try:
            s = s.cast(DATATYPES[s.name], strict=False)
            if s.name == "value":
                s = s.fill_null(value=invalid_value)
            elif s.name == "status":
                s = s.fill_null(default_quality)
        except KeyError as err:
            raise KeyError(f"Column Name {s.name} not found in Datatypes definition") from err
        except pl.ColumnNotFoundError:
            pass
    return s


class ZRXPMetadata(MetadataBaseModel):
    SANR: Optional[str] = Field(default=None, alias="stationNumber", description="Station Number")
    SNAME: Optional[str] = Field(default=None, alias="stationName", description="Station Name")
    SWATER: Optional[str] = Field(default=None, alias="water", description="River Name")
    CDASA: Optional[int] = Field(
        default=None, alias="dataLogger", description="Remote call logger/meter (DASA) number"
    )
    CDASANAME: Optional[str] = Field(
        default=None, alias="dataLoggerName", description="Remote call logger/meter (DASA) name"
    )
    CCHANNEL: Optional[str] = Field(
        default=None, alias="channelName", description="Remote call logger/meter (DASA) channel name"
    )
    CCHANNELNO: Optional[str] = Field(
        default=None, alias="channel", description="Remote call logger/meter (DASA) channel number"
    )
    CMW: Optional[int] = Field(default=None, alias="valuesPerDay", description="Values per day")
    CNAME: Optional[str] = Field(default=None, alias="parameterName", description="Parameter Name")
    CNR: Optional[str] = Field(default=None, alias="parameterNumber", description="Parameter Number")
    CUNIT: Optional[str] = Field(default=None, alias="unit", description="Parameter Unit")
    REXCHANGE: Optional[str] = Field(
        default=None, alias="exchangeNumber", description="Import number of import agent"
    )
    RINVAL: Optional[float] = Field(
        default=-777, alias="invalidValue", description="Value for missing/invalid data"
    )
    RTIMELVL: Optional[str] = Field(default=None, alias="timeLevel", description="Time Series time level")
    RTYPE: Optional[str] = Field(default=None, description="Time Series type")
    RSTATE: Optional[str] = Field(default=None, description="Time Series state")
    XVLID: Optional[Union[int, str]] = Field(
        default=None, alias="id", description="Time Series internal ID"
    )
    TSPATH: Optional[str] = Field(default=None, alias="tsPath", description="Time Series absolute path")
    CTAG: Optional[str] = Field(default=None, description="Special Tag")
    CTAGKEY: Optional[str] = Field(default=None, description="Special Tag key")
    XTRUNCATE: Optional[bool] = Field(default=None, description="Removes all TimeSeries data before import")
    MANDANT: Optional[str] = Field(default=None, description="AMC/SODA tenant")
    METCODE: Optional[str] = Field(default=None, description="metering code for energy market instance")
    METNUMBER: Optional[str] = Field(default=None, description="metering number")
    TASKID: Optional[str] = Field(default=None, description="AMC/SODA task id")
    TASKNAME: Optional[str] = Field(default=None, description="AMC/SODA task name")
    TASKSERIALID: Optional[str] = Field(default=None, description="AMC/SODA task serial id")
    EDIS: Optional[str] = Field(default=None, description="EDIS/OBIS code")
    TZ: Optional[str] = Field(default=None, alias="timezone", description="timezone")
    ZDATE: Optional[str] = Field(default=None, description="timestamp")
    ZRXPVERSION: Optional[str] = Field(default=None, description="ZRXP Version")
    ZRXPCREATOR: Optional[str] = Field(
        default=None, description="Name of the creation tool of the current ZRXP file"
    )
    SOURCESYSTEM: Optional[str] = Field(
        default=None, alias="sourceSystem", description="Designator of source system"
    )
    SOURCEID: Optional[str] = Field(
        default=None, alias="sourceId", description="Time Series identifier by this source"
    )
    DEFQUALITY: Optional[int] = Field(
        default=None, description="Default quality value if none has been assigned yet"
    )


def parse_timezone(timezone: str) -> str:
    """Parse ZRXP timezone strings into polars timezone strings."""
    if ("UTC" in timezone or "GMT" in timezone) and not timezone.startswith("Etc/"):
        if "+" in timezone:
            timezone = f"Etc/GMT-{int(timezone.split('+')[-1].split(')')[0].split(':')[0])}"
        elif "-" in timezone:
            timezone = f"Etc/GMT+{int(timezone.split('-')[-1].split(')')[0].split(':')[0])}"
    elif timezone == "MEZ":  # Localized German timezone aka CET
        return "CET"
    return timezone


class ZRXPData(BaseModel, arbitrary_types_allowed=True):
    data: Union[pl.DataFrame, pd.DataFrame]
    layout: list[str]
    metadata: ZRXPMetadata

    @classmethod
    def from_zrxp_rs(cls, zrxp: _ZRXPData, engine: Engine | Literal["polars", "pandas"]) -> ZRXPData:
        try:
            zrxp_metadata = model_validate(ZRXPMetadata, zrxp.metadata)
            timezone = parse_timezone(zrxp_metadata.TZ or "UTC")
            invalid_value = zrxp_metadata.RINVAL or -777
            default_quality = zrxp_metadata.DEFQUALITY or 200
            data = zrxp.data.select(
                pl.all().map_batches(
                    lambda s: convert_series(
                        s, timezone=timezone, invalid_value=invalid_value, default_quality=default_quality
                    )
                )
            )
        except pl.exceptions.ComputeError as e:
            raise ZRXPReadError(f"Invalid ZRXP. Error in Data. ({e})") from e

        return cls(
            data=apply_engine(data, engine),
            layout=zrxp.layout,
            metadata=zrxp_metadata,
        )
