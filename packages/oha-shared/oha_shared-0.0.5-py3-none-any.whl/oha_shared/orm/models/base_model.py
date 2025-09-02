"""
Base model class for all ORM models.
"""

from typing import Any, Dict, TypeVar
from sqlalchemy.orm import DeclarativeBase


T = TypeVar('T', bound='BaseModel')


class Base(DeclarativeBase):
    """Base class for declarative models with metadata."""
    pass


class BaseModel(Base):
    """
    Base model class that all ORM models should inherit from.
    
    Provides:
    - Common utility methods
    - Note: ID field and audit fields are now provided by AuditMixin
    """
    
    __abstract__ = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if value is not None:
                result[column.name] = value
        return result
    
    def __repr__(self) -> str:
        """String representation of the model."""
        class_name = self.__class__.__name__
        if hasattr(self, 'id'):
            return f"<{class_name}(id={self.id})>"
        return f"<{class_name}>"
    
    def __eq__(self, other: Any) -> bool:
        """Equality comparison."""
        if not isinstance(other, self.__class__):
            return False
        if hasattr(self, 'id') and hasattr(other, 'id'):
            return self.id == other.id
        return super().__eq__(other)
    
    def __hash__(self) -> int:
        """Hash based on ID if available."""
        if hasattr(self, 'id'):
            return hash((self.__class__, self.id))
        return super().__hash__()
