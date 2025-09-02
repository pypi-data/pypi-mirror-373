class FairoSDKException(Exception):
    """Base exception for all FairO SDK errors."""
    pass

class AuthenticationError(FairoSDKException):
    """Raised when there's an authentication problem."""
    pass