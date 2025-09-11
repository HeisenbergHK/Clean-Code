import os
from typing import Optional

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# Load environment variables from .env file
load_dotenv()


class DatabaseConnection:
    """Manages MongoDB connection and provides access to collections."""

    def __init__(self):
        # Load database configuration from environment variables
        self.database_name = os.getenv("MONGO_INITDB_DATABASE")
        self.username = os.getenv("MONGO_INITDB_ROOT_USERNAME")
        self.password = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
        self.host = os.getenv("MONGO_HOST")
        self.port = int(os.getenv("MONGO_PORT"))

        # Initialize client and database references
        self._client: Optional[AsyncIOMotorClient] = None
        self._db: Optional[AsyncIOMotorDatabase] = None

    def _get_client(self) -> AsyncIOMotorClient:
        """Get or create MongoDB client with connection parameters.

        Returns:
            AsyncIOMotorClient: MongoDB client instance
        """
        if self._client is None:
            self._client = AsyncIOMotorClient(
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
            )
        return self._client

    def get_database(self) -> AsyncIOMotorDatabase:
        """Get database instance.

        Returns:
            AsyncIOMotorDatabase: Database instance
        """
        if self._db is None:
            client = self._get_client()
            self._db = client[self.database_name]
        return self._db

    def get_user_collection(self):
        """Get users collection.

        Returns:
            Collection instance for users_affiliate
        """
        return self.get_database()["users_affiliate"]

    def get_wallet_collection(self):
        """Get wallet collection.

        Returns:
            Collection instance for users_wallet
        """
        return self.get_database()["users_wallet"]

    def get_payout_collection(self):
        """Get payout collection.

        Returns:
            Collection instance for payout_affiliate
        """
        return self.get_database()["payout_affiliate"]

    async def close(self):
        """Close database connection."""
        if self._client:
            self._client.close()


# Create global database connection instance
db_connection = DatabaseConnection()

# Create global references to database and collections for easy import
db = db_connection.get_database()
user_collection = db_connection.get_user_collection()
wallet_collection = db_connection.get_wallet_collection()
payout_collection = db_connection.get_payout_collection()
