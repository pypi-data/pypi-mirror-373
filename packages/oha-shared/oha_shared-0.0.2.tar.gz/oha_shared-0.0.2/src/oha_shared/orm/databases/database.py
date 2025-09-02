"""
Generic database connection and session management.
"""

from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy import create_engine, Engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from oha_shared.orm.exceptions import DatabaseConnectionError


class Database:
    """Generic database connection manager."""
    
    def __init__(
        self,
        database_url: str,
        echo: bool = False,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_timeout: int = 30,
        pool_recycle: int = 3600
    ):
        """
        Initialize database connection.
        
        Args:
            database_url: Database connection string
            echo: Enable SQL logging
            pool_size: Connection pool size
            max_overflow: Maximum overflow connections
            pool_timeout: Connection timeout
            pool_recycle: Connection recycle time
        """
        self.database_url = database_url
        self.echo = echo
        self.engine: Optional[Engine] = None
        self.session_factory: Optional[sessionmaker] = None
        
        # Connection pool settings
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
    
    def _create_engine(self) -> Engine:
        """Create SQLAlchemy engine. Can be overridden by subclasses."""
        return create_engine(
            self.database_url,
            echo=self.echo,
            poolclass=QueuePool,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            pool_timeout=self.pool_timeout,
            pool_recycle=self.pool_recycle,
            pool_pre_ping=True
        )
    
    def _test_connection(self, engine: Engine) -> None:
        """Test database connection. Can be overridden by subclasses."""
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    
    def connect(self) -> None:
        """Establish database connection."""
        try:
            self.engine = self._create_engine()
            self._test_connection(self.engine)
            
            self.session_factory = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )
            
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to connect to database: {str(e)}") from e
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            self.engine = None
            self.session_factory = None
    
    def get_session(self) -> Session:
        """Get a new database session."""
        if not self.session_factory:
            raise DatabaseConnectionError("Database not connected. Call connect() first.")
        return self.session_factory()
    
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Context manager for database sessions with automatic rollback on error."""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create_tables(self, base) -> None:
        """Create all tables for the given base."""
        if not self.engine:
            raise DatabaseConnectionError("Database not connected. Call connect() first.")
        base.metadata.create_all(self.engine)
    
    def drop_tables(self, base) -> None:
        """Drop all tables for the given base."""
        if not self.engine:
            raise DatabaseConnectionError("Database not connected. Call connect() first.")
        base.metadata.drop_all(self.engine)
    
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self.engine is not None and self.engine.pool.checkedin() > 0
    
    def __enter__(self):
        """Context manager entry."""
        if not self.engine:
            self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
