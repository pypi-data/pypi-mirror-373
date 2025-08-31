import abc

class Database(abc.ABC):
    """
    An abstract base class for database connections.
    
    This class defines a standard interface that all database
    connectors in WinUp should follow, ensuring a consistent API
    for connecting, executing queries, and closing connections.
    """

    @abc.abstractmethod
    def connect(self, **kwargs):
        """
        Establish a connection to the database.
        
        This method should handle the specifics of connecting to a 
        particular database type (e.g., file path for SQLite,
        host/user/password for PostgreSQL).
        """
        pass

    @abc.abstractmethod
    def disconnect(self):
        """Close the connection to the database."""
        pass

    @abc.abstractmethod
    def execute(self, query: str, params: tuple = ()):
        """
        Execute a SQL query.
        
        Args:
            query: The SQL query string to execute.
            params: A tuple of parameters to safely bind to the query.
        
        Returns:
            The result of the query, typically a list of rows.
        """
        pass

    def __enter__(self):
        """Allow the use of 'with' statement for automatic connection management."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Automatically close the connection when exiting a 'with' block."""
        self.disconnect() 