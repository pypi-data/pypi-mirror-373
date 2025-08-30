import psycopg2
from .database import Database

class PostgresConnector(Database):
    """A concrete implementation of the Database interface for PostgreSQL."""

    def __init__(self, dbname, user, password, host='localhost', port=5432):
        """Initializes the connector with PostgreSQL connection details."""
        self.conn_params = {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'port': port
        }
        self.conn = None

    def connect(self):
        """Establishes a connection to the PostgreSQL database."""
        if self.conn and not self.conn.closed:
            return
        try:
            self.conn = psycopg2.connect(**self.conn_params)
        except psycopg2.Error as e:
            print(f"PostgreSQL connection error: {e}")
            raise

    def disconnect(self):
        """Closes the active database connection."""
        if self.conn and not self.conn.closed:
            self.conn.close()
            self.conn = None

    def execute(self, query: str, params: tuple = ()):
        """Executes a SQL query on the PostgreSQL database."""
        if not self.conn or self.conn.closed:
            raise RuntimeError("Database is not connected. Call connect() first or use a 'with' statement.")
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                
                if cursor.description:
                    return cursor.fetchall()
                return []
        except psycopg2.Error as e:
            print(f"PostgreSQL query failed: {e}")
            self.conn.rollback() # Rollback on error
            raise
        finally:
            self.conn.commit() # Commit changes if the block succeeds 