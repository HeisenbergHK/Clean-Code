import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.JWT_authentication import ConfigManager, JWTHandler, AuthenticationService


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_config_manager():
    """Mock configuration manager for testing."""
    config = MagicMock(spec=ConfigManager)
    config.jwt_secret = "test-secret-key"
    config.jwt_algorithm = "HS256"
    config.jwt_expiration_minutes = 30
    return config


@pytest.fixture
def mock_jwt_handler(mock_config_manager):
    """Mock JWT handler for testing."""
    return JWTHandler(mock_config_manager)


@pytest.fixture
def mock_auth_service(mock_jwt_handler):
    """Mock authentication service for testing."""
    return AuthenticationService(mock_jwt_handler)


@pytest.fixture
def mock_user_collection():
    """Mock user collection for database testing."""
    collection = AsyncMock()
    return collection


@pytest.fixture
def mock_payout_collection():
    """Mock payout collection for database testing."""
    collection = AsyncMock()
    return collection


@pytest.fixture
def mock_wallet_collection():
    """Mock wallet collection for database testing."""
    collection = AsyncMock()
    return collection


@pytest.fixture
def sample_user():
    """Sample user data for testing."""
    return {
        "_id": "507f1f77bcf86cd799439011",
        "email": "admin@example.com",
        "user_type": "admin",
        "password": b"hashed_password"
    }


@pytest.fixture
def sample_payout():
    """Sample payout data for testing."""
    return {
        "_id": "507f1f77bcf86cd799439012",
        "user_id": "507f1f77bcf86cd799439011",
        "amount": 150.00,
        "status": "pending",
        "user_type": "affiliate",
        "created": "2024-01-15T10:30:00Z",
        "payment_date": "2024-01-20T10:30:00Z"
    }