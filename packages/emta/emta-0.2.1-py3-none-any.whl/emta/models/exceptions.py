"""Exception models for the Eastmoney Trading Library."""


class LoginError(Exception):
    """Exception raised for login errors"""

    pass


class ValidateKeyError(Exception):
    """Exception raised for validate key errors"""

    pass


class TradingError(Exception):
    """Exception raised for trading errors"""

    pass
