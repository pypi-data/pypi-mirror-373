import pymongo

class MongoConnector:
    """A connector for interacting with a MongoDB database."""

    def __init__(self, connection_string: str, db_name: str):
        """
        Initializes the connector with a MongoDB connection string and database name.
        
        Args:
            connection_string: The URI to connect to MongoDB (e.g., "mongodb://localhost:27017/").
            db_name: The name of the database to use.
        """
        self.client = None
        self.db = None
        self.connection_string = connection_string
        self.db_name = db_name

    def connect(self):
        """Establishes a connection to the MongoDB server."""
        if self.client:
            return
        try:
            self.client = pymongo.MongoClient(self.connection_string)
            self.db = self.client[self.db_name]
            # The ismaster command is cheap and does not require auth.
            self.client.admin.command('ismaster')
            print("MongoDB connection successful.")
        except pymongo.errors.ConnectionFailure as e:
            print(f"MongoDB connection error: {e}")
            self.client = None
            self.db = None
            raise

    def disconnect(self):
        """Closes the connection to the MongoDB server."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None

    def get_collection(self, collection_name: str):
        """Returns a handle to a collection."""
        if not self.db:
            raise RuntimeError("Not connected to MongoDB. Call connect() first.")
        return self.db[collection_name]

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect() 