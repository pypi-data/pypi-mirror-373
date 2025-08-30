import pymysql
from .database import Database

class MySQLConnector(Database):
    """A concrete implementation of the Database interface for MySQL."""

    def __init__(self, db, user, password, host='localhost', port=3306):
        """Initializes the connector with MySQL connection details."""
        self.conn_params = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'db': db,
            'cursorclass': pymysql.cursors.DictCursor  # Fetch results as dictionaries
        }
        self.conn = None

    def connect(self):
        """Establishes a connection to the MySQL database."""
        if self.conn and self.conn.open:
            return
        try:
            self.conn = pymysql.connect(**self.conn_params)
        except pymysql.Error as e:
            print(f"MySQL connection error: {e}")
            raise

    def disconnect(self):
        """Closes the active database connection."""
        if self.conn and self.conn.open:
            self.conn.close()
            self.conn = None

    def execute(self, query: str, params: tuple = ()):
        """Executes a SQL query on the MySQL database."""
        if not self.conn or not self.conn.open:
            raise RuntimeError("Database is not connected. Call connect() first or use a 'with' statement.")
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchall()
                self.conn.commit()
                return result
        except pymysql.Error as e:
            print(f"MySQL query failed: {e}")
            self.conn.rollback()
            raise 