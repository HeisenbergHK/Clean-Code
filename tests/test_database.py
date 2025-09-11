import pytest
from unittest.mock import patch, MagicMock
from app.database import DatabaseConnection


class TestDatabaseConnection:
    """Test cases for DatabaseConnection class."""
    
    @patch.dict('os.environ', {
        'MONGO_INITDB_DATABASE': 'test_db',
        'MONGO_INITDB_ROOT_USERNAME': 'test_user',
        'MONGO_INITDB_ROOT_PASSWORD': 'test_pass',
        'MONGO_HOST': 'localhost',
        'MONGO_PORT': '27017'
    })
    def test_database_connection_initialization(self):
        db_conn = DatabaseConnection()
        assert db_conn.database_name == 'test_db'
        assert db_conn.username == 'test_user'
        assert db_conn.password == 'test_pass'
        assert db_conn.host == 'localhost'
        assert db_conn.port == 27017
    
    @patch('app.database.AsyncIOMotorClient')
    def test_get_client(self, mock_client):
        db_conn = DatabaseConnection()
        client = db_conn._get_client()
        
        mock_client.assert_called_once_with(
            host=db_conn.host,
            port=db_conn.port,
            username=db_conn.username,
            password=db_conn.password,
        )
        assert db_conn._client is not None
    
    @patch('app.database.AsyncIOMotorClient')
    def test_get_database(self, mock_client):
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        db_conn = DatabaseConnection()
        database = db_conn.get_database()
        
        assert database == mock_client_instance[db_conn.database_name]
    
    def test_get_user_collection(self):
        db_conn = DatabaseConnection()
        with patch.object(db_conn, 'get_database') as mock_get_db:
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            
            collection = db_conn.get_user_collection()
            assert collection == mock_db["users_affiliate"]
    
    def test_get_wallet_collection(self):
        db_conn = DatabaseConnection()
        with patch.object(db_conn, 'get_database') as mock_get_db:
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            
            collection = db_conn.get_wallet_collection()
            assert collection == mock_db["users_wallet"]
    
    def test_get_payout_collection(self):
        db_conn = DatabaseConnection()
        with patch.object(db_conn, 'get_database') as mock_get_db:
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            
            collection = db_conn.get_payout_collection()
            assert collection == mock_db["payout_affiliate"]
    
    @pytest.mark.asyncio
    async def test_close_connection(self):
        db_conn = DatabaseConnection()
        mock_client = MagicMock()
        db_conn._client = mock_client
        
        await db_conn.close()
        mock_client.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close_connection_no_client(self):
        db_conn = DatabaseConnection()
        # Should not raise an exception when client is None
        await db_conn.close()