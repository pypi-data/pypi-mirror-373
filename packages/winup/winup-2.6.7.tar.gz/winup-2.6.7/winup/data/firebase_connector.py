import firebase_admin
from firebase_admin import credentials, firestore

class FirebaseConnector:
    """A connector for interacting with Google Firebase services, primarily Firestore."""

    def __init__(self, service_account_key_path: str):
        """
        Initializes the connector with a Firebase service account key.

        Args:
            service_account_key_path: The file path to your Firebase service account JSON key.
        """
        self.service_account_key_path = service_account_key_path
        self._app = None
        self.db = None

    def connect(self):
        """Initializes the Firebase Admin SDK."""
        if self._app:
            return
        try:
            cred = credentials.Certificate(self.service_account_key_path)
            self._app = firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            print("Firebase connection successful.")
        except Exception as e:
            print(f"Firebase connection error: {e}")
            self._app = None
            self.db = None
            raise

    def disconnect(self):
        """Deletes the Firebase app instance to clean up resources."""
        if self._app:
            firebase_admin.delete_app(self._app)
            self._app = None
            self.db = None

    def get_collection(self, collection_name: str):
        """
        Returns a reference to a Firestore collection.

        This reference can be used to add, get, update, or delete documents.
        """
        if not self.db:
            raise RuntimeError("Not connected to Firebase. Call connect() first.")
        return self.db.collection(collection_name)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect() 