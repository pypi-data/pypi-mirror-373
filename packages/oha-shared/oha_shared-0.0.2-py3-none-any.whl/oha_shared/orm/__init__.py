"""
ORM wrapper package for OHA Shared.
"""

from .models import Base, BaseModel
from .mixins import AuditMixin, TextSearchMixin
from .databases import Database, PostgreSQLConnection
from .repositories import BaseRepository
from .units import UnitOfWork
from .exceptions import ORMException, ValidationError, NotFoundError

__all__ = [
    # Models
    "Base",
    "BaseModel",
    
    # Mixins
    "AuditMixin",
    "TextSearchMixin",
    
    # Databases
    "Database",
    "PostgreSQLConnection",
    
    # Repositories
    "BaseRepository",
    
    # Units of Work
    "UnitOfWork",
    
    # Exceptions
    "ORMException",
    "ValidationError",
    "NotFoundError",
]
