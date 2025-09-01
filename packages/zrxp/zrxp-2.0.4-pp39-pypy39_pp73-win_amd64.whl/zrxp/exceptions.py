class ZRXPReadError(Exception):
    def __init__(self, message: str = "Invalid ZRXP") -> None:
        super().__init__(message)
