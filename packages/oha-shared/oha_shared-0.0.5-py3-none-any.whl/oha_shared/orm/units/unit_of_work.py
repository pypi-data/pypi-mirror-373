"""
Unit of work class for transaction management.
"""

from contextlib import contextmanager
from typing import Generator, Any, Callable, List
from sqlalchemy.orm import Session


class UnitOfWork:
    """Unit of work class providing transaction management."""
    
    def __init__(self, session: Session):
        """
        Initialize unit of work.
        
        Args:
            session: Database session
        """
        self.session = session
    
    # ===== BASIC TRANSACTION OPERATIONS =====
    
    def commit(self) -> None:
        """Commit the current transaction."""
        self.session.commit()
    
    def rollback(self) -> None:
        """Rollback the current transaction."""
        self.session.rollback()
    
    def flush(self) -> None:
        """Flush pending changes to the database."""
        self.session.flush()
    
    # ===== CONTEXT MANAGERS =====
    
    @contextmanager
    def transaction(self) -> Generator[Session, None, None]:
        """Context manager for transactions with automatic rollback on error."""
        try:
            yield self.session
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
    
    @contextmanager
    def nested_transaction(self) -> Generator[Session, None, None]:
        """Context manager for nested transactions (savepoints)."""
        savepoint = self.session.begin_nested()
        try:
            yield self.session
            savepoint.commit()
        except Exception:
            savepoint.rollback()
            raise
    
    # ===== UTILITY METHODS =====
    
    def execute_in_transaction(self, func: Callable[[Session], Any]) -> Any:
        """Execute a function within a transaction."""
        with self.transaction() as session:
            return func(session)
    
    def bulk_operation(self, operations: List[Callable[[Session], None]]) -> None:
        """Execute multiple operations in a single transaction."""
        with self.transaction() as session:
            for operation in operations:
                operation(session)
    
    def is_in_transaction(self) -> bool:
        """Check if currently in a transaction."""
        return self.session.in_transaction()
    
    def close(self) -> None:
        """Close the session."""
        self.session.close()
