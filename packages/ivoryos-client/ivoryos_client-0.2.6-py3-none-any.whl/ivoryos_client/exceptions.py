class IvoryosError(Exception):
    """Base exception for IvoryOS client errors"""
    pass


class AuthenticationError(IvoryosError):
    """Raised when authentication fails"""
    pass


class ConnectionError(IvoryosError):
    """Raised when connection to IvoryOS fails"""
    pass


class WorkflowError(IvoryosError):
    """Raised when workflow operations fail"""
    pass


class TaskError(IvoryosError):
    """Raised when task operations fail"""
    pass