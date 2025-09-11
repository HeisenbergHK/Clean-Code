import pytest
import jwt
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException
from app.JWT_authentication import (
    ConfigManager, JWTHandler, AuthenticationService, 
    QueryProcessor, AuthenticationFactory
)


class TestConfigManager:
    """Test cases for ConfigManager class."""
    
    @patch.dict('os.environ', {
        'JWT_SECRET': 'test-secret',
        'JWT_ALGORITHM': 'HS256',
        'JWT_EXPIRATION_MINUTES': '60'
    })
    def test_config_manager_initialization(self):
        config = ConfigManager()
        assert config.jwt_secret == 'test-secret'
        assert config.jwt_algorithm == 'HS256'
        assert config.jwt_expiration_minutes == 60


class TestJWTHandler:
    """Test cases for JWTHandler class."""
    
    def test_decode_valid_token(self, mock_config_manager):
        handler = JWTHandler(mock_config_manager)
        payload = {"sub": "test@example.com", "exp": 9999999999}
        token = jwt.encode(payload, "test-secret-key", algorithm="HS256")
        
        result = handler.decode_token(token)
        assert result["sub"] == "test@example.com"
    
    def test_decode_invalid_token(self, mock_config_manager):
        handler = JWTHandler(mock_config_manager)
        result = handler.decode_token("invalid-token")
        assert result == {}
    
    def test_extract_token_from_authorization(self, mock_jwt_handler):
        token = mock_jwt_handler.extract_token_from_authorization("Bearer test-token")
        assert token == "test-token"
        
        token = mock_jwt_handler.extract_token_from_authorization("test-token")
        assert token == "test-token"
    
    def test_get_email_from_token_payload_valid(self, mock_jwt_handler):
        payload = {"sub": "test@example.com"}
        email = mock_jwt_handler.get_email_from_token_payload(payload)
        assert email == "test@example.com"
    
    def test_get_email_from_token_payload_missing_sub(self, mock_jwt_handler):
        payload = {"user": "test@example.com"}
        with pytest.raises(HTTPException) as exc_info:
            mock_jwt_handler.get_email_from_token_payload(payload)
        assert exc_info.value.status_code == 400


class TestAuthenticationService:
    """Test cases for AuthenticationService class."""
    
    @pytest.mark.asyncio
    async def test_get_email_from_token_success(self, mock_auth_service):
        with patch.object(mock_auth_service.jwt_handler, 'extract_token_from_authorization', return_value="test-token"), \
             patch.object(mock_auth_service.jwt_handler, 'decode_token', return_value={"sub": "test@example.com"}), \
             patch.object(mock_auth_service.jwt_handler, 'get_email_from_token_payload', return_value="test@example.com"):
            
            email = await mock_auth_service.get_email_from_token("Bearer test-token")
            assert email == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_check_user_is_admin_success(self, mock_auth_service, sample_user):
        with patch.object(mock_auth_service, 'get_email_from_token', return_value="admin@example.com"), \
             patch('app.JWT_authentication.user_collection') as mock_collection:
            
            mock_collection.find_one.return_value = sample_user
            result = await mock_auth_service.check_user_is_admin("Bearer test-token")
            assert result == sample_user
    
    @pytest.mark.asyncio
    async def test_check_user_is_admin_user_not_found(self, mock_auth_service):
        with patch.object(mock_auth_service, 'get_email_from_token', return_value="nonexistent@example.com"), \
             patch('app.JWT_authentication.user_collection') as mock_collection:
            
            mock_collection.find_one.return_value = None
            with pytest.raises(HTTPException) as exc_info:
                await mock_auth_service.check_user_is_admin("Bearer test-token")
            assert exc_info.value.status_code == 404
    
    @pytest.mark.asyncio
    async def test_check_user_is_admin_not_admin(self, mock_auth_service):
        user = {"email": "user@example.com", "user_type": "user"}
        with patch.object(mock_auth_service, 'get_email_from_token', return_value="user@example.com"), \
             patch('app.JWT_authentication.user_collection') as mock_collection:
            
            mock_collection.find_one.return_value = user
            with pytest.raises(HTTPException) as exc_info:
                await mock_auth_service.check_user_is_admin("Bearer test-token")
            assert exc_info.value.status_code == 400


class TestQueryProcessor:
    """Test cases for QueryProcessor class."""
    
    @pytest.mark.asyncio
    async def test_get_status_list_from_query(self):
        processor = QueryProcessor()
        result = await processor.get_status_list_from_query("pending,approved,rejected")
        assert result == ["pending", "approved", "rejected"]
        
        result = await processor.get_status_list_from_query("pending, approved , rejected ")
        assert result == ["pending", "approved", "rejected"]


class TestAuthenticationFactory:
    """Test cases for AuthenticationFactory class."""
    
    def test_create_authentication_service(self):
        service = AuthenticationFactory.create_authentication_service()
        assert isinstance(service, AuthenticationService)
    
    def test_create_query_processor(self):
        processor = AuthenticationFactory.create_query_processor()
        assert isinstance(processor, QueryProcessor)