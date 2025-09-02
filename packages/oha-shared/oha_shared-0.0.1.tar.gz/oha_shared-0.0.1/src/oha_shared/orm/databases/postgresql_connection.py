"""
PostgreSQL connection manager.
"""

from oha_shared.orm.databases.database import Database


class PostgreSQLConnection:
    """Simple PostgreSQL connection manager."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "postgres",
        username: str = "postgres",
        password: str = "",
        **kwargs
    ):
        """
        Initialize PostgreSQL connection parameters.
        
        Args:
            host: Database host
            port: Database port
            database: Database name
            username: Database username
            password: Database password
            **kwargs: Additional database parameters
        """
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.kwargs = kwargs
        self._db = None
    
    def connect(self) -> Database:
        """
        Connect to PostgreSQL database.
        
        Returns:
            Connected Database instance
        """
        database_url = f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        self._db = Database(database_url, **self.kwargs)
        self._db.connect()
        return self._db
    
    def get_connection_string(self) -> str:
        """Get the PostgreSQL connection string."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._db is not None and self._db.is_connected() > 0