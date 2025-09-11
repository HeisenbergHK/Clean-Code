import pytest
from datetime import datetime
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import router


class TestPayoutEndpoint:
    """Test cases for the payout endpoint."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(router)
    
    @pytest.mark.asyncio
    async def test_all_payout_basic_filters(self):
        """Test payout endpoint with basic filters."""
        mock_response = {
            "page": 1,
            "pageSize": 3,
            "totalPages": 1,
            "totalDocs": 2,
            "results": [
                {
                    "id": "507f1f77bcf86cd799439011",
                    "userId": "507f1f77bcf86cd799439012",
                    "amount": 150.00,
                    "status": "pending"
                }
            ]
        }
        
        with patch('app.main.auth_service.check_user_is_admin', return_value={"user_type": "admin"}), \
             patch('app.main.create_paginate_response', return_value=mock_response) as mock_paginate:
            
            from app.main import all_payout
            
            result = await all_payout(
                statuses="pending,approved",
                page=1,
                user_type="affiliate"
            )
            
            # Verify the function was called with correct match parameters
            mock_paginate.assert_called_once()
            call_args = mock_paginate.call_args
            match_param = call_args[0][2]  # Third parameter is match
            
            assert "status" in match_param
            assert match_param["status"]["$in"] == ["pending", "approved"]
            assert match_param["user_type"] == "affiliate"
            assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_all_payout_date_filters(self):
        """Test payout endpoint with date filters."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        payment_start = datetime(2024, 1, 15)
        payment_end = datetime(2024, 1, 30)
        
        mock_response = {"page": 1, "results": []}
        
        with patch('app.main.auth_service.check_user_is_admin', return_value={"user_type": "admin"}), \
             patch('app.main.create_paginate_response', return_value=mock_response) as mock_paginate, \
             patch('app.main.query_processor.get_status_list_from_query', return_value=["pending"]):
            
            from app.main import all_payout
            
            result = await all_payout(
                page=1,
                start_date=start_date,
                end_date=end_date,
                payment_start_date=payment_start,
                payment_end_date=payment_end,
                statuses="pending"
            )
            
            # Verify date filters are applied correctly
            call_args = mock_paginate.call_args
            match_param = call_args[0][2]
            
            assert "created" in match_param
            assert match_param["created"]["$gte"] == start_date
            assert match_param["created"]["$lte"] == end_date
            
            assert "payment_date" in match_param
            assert match_param["payment_date"]["$gte"] == payment_start
            assert match_param["payment_date"]["$lte"] == payment_end
    
    @pytest.mark.asyncio
    async def test_all_payout_no_filters(self):
        """Test payout endpoint without filters."""
        mock_response = {"page": None, "results": []}
        
        with patch('app.main.auth_service.check_user_is_admin', return_value={"user_type": "admin"}), \
             patch('app.main.create_paginate_response', return_value=mock_response) as mock_paginate:
            
            from app.main import all_payout
            
            result = await all_payout()
            
            # Verify empty match is passed when no filters
            call_args = mock_paginate.call_args
            match_param = call_args[0][2]
            
            # Should be empty dict or only contain empty date filters
            assert len([k for k, v in match_param.items() if v]) == 0
    
    @pytest.mark.asyncio
    async def test_all_payout_partial_date_filters(self):
        """Test payout endpoint with partial date filters."""
        start_date = datetime(2024, 1, 1)
        
        mock_response = {"page": 1, "results": []}
        
        with patch('app.main.auth_service.check_user_is_admin', return_value={"user_type": "admin"}), \
             patch('app.main.create_paginate_response', return_value=mock_response) as mock_paginate:
            
            from app.main import all_payout
            
            result = await all_payout(
                page=1,
                start_date=start_date
            )
            
            # Verify only start_date filter is applied
            call_args = mock_paginate.call_args
            match_param = call_args[0][2]
            
            assert "created" in match_param
            assert match_param["created"]["$gte"] == start_date
            assert "$lte" not in match_param["created"]
            
            # payment_date should not be in match since no payment dates provided
            assert "payment_date" not in match_param


class TestMainModule:
    """Test cases for main module configuration."""
    
    def test_router_initialization(self):
        """Test that FastAPI router is properly initialized."""
        from app.main import router
        from fastapi import FastAPI
        
        assert isinstance(router, FastAPI)
    
    def test_auth_service_initialization(self):
        """Test that authentication service is properly initialized."""
        from app.main import auth_service
        from app.JWT_authentication import AuthenticationService
        
        assert isinstance(auth_service, AuthenticationService)
    
    def test_query_processor_initialization(self):
        """Test that query processor is properly initialized."""
        from app.main import query_processor
        from app.JWT_authentication import QueryProcessor
        
        assert isinstance(query_processor, QueryProcessor)