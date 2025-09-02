"""
Custom ORM exceptions for better error handling and debugging.
"""


class ORMException(Exception):
    """Base exception for all ORM-related errors."""
    pass


class ValidationError(ORMException):
    """Raised when model validation fails."""
    pass


class NotFoundError(ORMException):
    """Raised when a requested entity is not found."""
    pass


class DatabaseConnectionError(ORMException):
    """Raised when database connection fails."""
    pass


class TransactionError(ORMException):
    """Raised when transaction operations fail."""
    pass


class QueryError(ORMException):
    """Raised when query execution fails."""
    pass
