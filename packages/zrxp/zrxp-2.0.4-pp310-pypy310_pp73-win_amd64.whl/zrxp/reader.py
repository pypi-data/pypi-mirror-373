from __future__ import annotations

import logging
from pathlib import Path
from typing import Literal

from ._core import ZRXPData as _ZRXPData
from ._core import _read_zrxp
from .data import Engine, ZRXPData
from .exceptions import ZRXPReadError

# TODO: What if no values?; whitespace in layout keys
logger = logging.getLogger(__name__)


def read(
    filename: str | Path, engine: Engine | Literal["polars", "pandas"] = Engine.PANDAS
) -> list[ZRXPData]:
    """
    Reads a ZRXP file

    :param filename: Path to the ZRXP file to be read
    :param engine: The engine to be used for processing the data. Polars is recommended
    :return: List of the ZRXP Data
    """
    if not Path(filename).is_file():
        raise FileNotFoundError(f"File {filename} not found")

    try:
        rs_df: list[_ZRXPData] = _read_zrxp(str(filename))
    except ValueError as e:
        raise ZRXPReadError(str(e)) from e
    errors = []
    results = []
    for dff in rs_df:
        try:
            results.append(ZRXPData.from_zrxp_rs(dff, engine))
        except Exception as e:
            errors.append(e)
    if not results and errors:
        raise ZRXPReadError("ZRXPData could not be parsed") from errors[0]
    if errors:
        logger.warning("Encountered %d errors parsging the ZRXP file: %s", len(errors), errors)

    return results
