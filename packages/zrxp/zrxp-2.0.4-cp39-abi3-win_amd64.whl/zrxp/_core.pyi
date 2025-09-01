import polars as pl

class ZRXPData:
    """
    Rust object holding the ZRXPData as polars.DataFrame and a dict with metadata.
    """
    @property
    def data(self) -> pl.DataFrame: ...
    @property
    def layout(self) -> list[str]: ...
    @property
    def metadata(self) -> dict[str, str]: ...

def _read_zrxp(filename: str) -> list[ZRXPData]:
    """
    Reads the zrxp file and parses it into polars DataFrames and metadata dicts.

    Args:
        filename: The zrxp file to read.

    Returns:
        A list of ZRXPData objects.
    """
