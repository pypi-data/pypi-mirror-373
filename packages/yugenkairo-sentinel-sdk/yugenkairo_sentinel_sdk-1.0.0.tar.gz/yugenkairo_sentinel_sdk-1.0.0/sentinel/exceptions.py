class SentinelError(Exception):
    """
    Base exception for Sentinel SDK errors
    """
    pass

class SecurityError(SentinelError):
    """
    Exception raised for security violations
    """
    pass

class PolicyError(SentinelError):
    """
    Exception raised for policy violations
    """
    pass

class NetworkError(SentinelError):
    """
    Exception raised for network connectivity issues
    """
    pass

class ValidationError(SentinelError):
    """
    Exception raised for input validation failures
    """
    pass