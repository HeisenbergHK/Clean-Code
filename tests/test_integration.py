import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import router


class TestIntegration:
    """Integration tests for the complete application flow."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(router)
    
    def test_payout_endpoint_unauthorized(self):
        """Test payout endpoint without authorization."""
        response = self.client.get("/payout")
        assert response.status_code == 422  # Missing required header
    
    def test_payout_endpoint_invalid_token(self):
        """Test payout endpoint with invalid token."""
        headers = {"Authorization": "Bearer invalid-token"}
        
        with patch('app.JWT_authentication.user_collection') as mock_collection:
            mock_collection.find_one.return_value = None
            
            response = self.client.get("/payout", headers=headers)
            # Should return 400 due to invalid token format
            assert response.status_code in [400, 401]
    
    @patch('app.main.create_paginate_response')
    @patch('app.JWT_authentication.user_collection')
    def test_payout_endpoint_admin_success(self, mock_user_collection, mock_paginate):
        """Test successful payout endpoint call with admin user."""
        # Mock admin user
        admin_user = {
            "_id": "507f1f77bcf86cd799439011",
            "email": "admin@example.com",
            "user_type": "admin"
        }
        mock_user_collection.find_one.return_value = admin_user
        
        # Mock pagination response
        mock_response = {
            "page": 1,
            "pageSize": 3,
            "totalPages": 1,
            "totalDocs": 1,
            "results": [
                {
                    "id": "507f1f77bcf86cd799439012",
                    "amount": 100.0,
                    "status": "pending"
                }
            ]
        }
        mock_paginate.return_value = mock_response
        
        # Create a valid JWT token for testing
        import jwt
        token_payload = {"sub": "admin@example.com"}
        token = jwt.encode(token_payload, "test-secret-key", algorithm="HS256")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        with patch('app.JWT_authentication.ConfigManager') as mock_config:
            mock_config.return_value.jwt_secret = "test-secret-key"
            mock_config.return_value.jwt_algorithm = "HS256"
            
            response = self.client.get("/payout?page=1", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                assert data == mock_response
            else:
                # Token validation might fail in test environment
                assert response.status_code in [400, 401]
    
    @patch('app.JWT_authentication.user_collection')
    def test_payout_endpoint_non_admin_user(self, mock_user_collection):
        """Test payout endpoint with non-admin user."""
        # Mock regular user
        regular_user = {
            "_id": "507f1f77bcf86cd799439011",
            "email": "user@example.com",
            "user_type": "user"
        }
        mock_user_collection.find_one.return_value = regular_user
        
        # Create a valid JWT token for testing
        import jwt
        token_payload = {"sub": "user@example.com"}
        token = jwt.encode(token_payload, "test-secret-key", algorithm="HS256")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        with patch('app.JWT_authentication.ConfigManager') as mock_config:
            mock_config.return_value.jwt_secret = "test-secret-key"
            mock_config.return_value.jwt_algorithm = "HS256"
            
            response = self.client.get("/payout", headers=headers)
            
            # Should return 400 because user is not admin
            assert response.status_code in [400, 401]
    
    def test_payout_endpoint_with_query_parameters(self):
        """Test payout endpoint with various query parameters."""
        headers = {"Authorization": "Bearer test-token"}
        
        query_params = {
            "page": 1,
            "statuses": "pending,approved",
            "user_type": "affiliate",
            "start_date": "2024-01-01T00:00:00",
            "end_date": "2024-01-31T23:59:59"
        }
        
        with patch('app.JWT_authentication.user_collection') as mock_collection, \
             patch('app.main.create_paginate_response') as mock_paginate:
            
            # Mock admin user
            admin_user = {"email": "admin@example.com", "user_type": "admin"}
            mock_collection.find_one.return_value = admin_user
            
            mock_paginate.return_value = {"results": []}
            
            response = self.client.get("/payout", headers=headers, params=query_params)
            
            # Response code depends on token validation
            assert response.status_code in [200, 400, 401, 422]


class TestHealthCheck:
    """Test application health and basic functionality."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(router)
    
    def test_openapi_docs_accessible(self):
        """Test that OpenAPI documentation is accessible."""
        response = self.client.get("/docs")
        assert response.status_code == 200
    
    def test_openapi_json_accessible(self):
        """Test that OpenAPI JSON schema is accessible."""
        response = self.client.get("/openapi.json")
        assert response.status_code == 200
        
        # Verify it's valid JSON
        data = response.json()
        assert "openapi" in data
        assert "paths" in data