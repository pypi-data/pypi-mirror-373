import sqlite3
from .database import Database

class SQLiteConnector(Database):
    """A concrete implementation of the Database interface for SQLite."""

    def __init__(self, db_path: str):
        """
        Initializes the connector with the path to the SQLite database file.
        
        Args:
            db_path: The file path, e.g., 'my_app.db' or ':memory:' for an in-memory db.
        """
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """Establishes a connection to the SQLite database file."""
        if self.conn:
            return
        try:
            self.conn = sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            raise

    def disconnect(self):
        """Closes the active database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute(self, query: str, params: tuple = ()):
        """
        Executes a SQL query on the SQLite database.
        
        Returns:
            The cursor object after execution. This allows access to results
            via cursor.fetchall() or properties like cursor.lastrowid.
        """
        if not self.conn:
            raise RuntimeError("Database is not connected. Call connect() first or use a 'with' statement.")
        
        try:
            with self.conn: # Use context manager for automatic commit/rollback
                cursor = self.conn.cursor()
                cursor.execute(query, params)
                return cursor
        except sqlite3.Error as e:
            print(f"Query failed: {e}")
            raise 