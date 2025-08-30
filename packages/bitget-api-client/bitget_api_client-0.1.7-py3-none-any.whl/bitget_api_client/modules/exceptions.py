class BitgetAPIException(Exception):
    """Base exception for Bitget API errors."""
    def __init__(self, message, code=None, http_status_code=None):
        super().__init__(message)
        self.code = code
        self.http_status_code = http_status_code

class BitgetAPIAuthException(BitgetAPIException):
    """Exception for authentication-related Bitget API errors."""
    pass

class BitgetAPIParameterException(BitgetAPIException):
    """Exception for parameter-related Bitget API errors."""
    pass

class BitgetAPINetworkException(BitgetAPIException):
    """Exception for network-related errors during API calls."""
    pass

class BitgetAPIWebSocketException(BitgetAPIException):
    """Exception for WebSocket-related Bitget API errors."""
    pass
