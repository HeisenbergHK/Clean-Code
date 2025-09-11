import pytest
import datetime
from unittest.mock import patch, AsyncMock, MagicMock
from bson.objectid import ObjectId
from fastapi import HTTPException
from app.tools import (
    check_is_valid_objectId, create_paginate_response, paginate_results,
    check_available_balance, snake_to_camel, convert_dict_camel_case,
    paginate_documents
)


class TestObjectIdValidation:
    """Test cases for ObjectId validation."""
    
    @pytest.mark.asyncio
    async def test_valid_object_id(self):
        valid_id = "507f1f77bcf86cd799439011"
        result = await check_is_valid_objectId(valid_id)
        assert isinstance(result, ObjectId)
        assert str(result) == valid_id
    
    @pytest.mark.asyncio
    async def test_invalid_object_id(self):
        invalid_id = "invalid-id"
        with pytest.raises(HTTPException) as exc_info:
            await check_is_valid_objectId(invalid_id)
        assert exc_info.value.status_code == 400


class TestPaginationResponse:
    """Test cases for pagination response creation."""
    
    @pytest.mark.asyncio
    async def test_create_paginate_response_with_page(self):
        mock_collection = AsyncMock()
        match = {"status": "pending"}
        
        with patch('app.tools.paginate_results', return_value=(1, 10, [])) as mock_paginate:
            result = await create_paginate_response(1, mock_collection, match)
            
            assert result["page"] == 1
            assert result["pageSize"] == 3
            assert result["totalPages"] == 4  # ceil(10/3)
            assert result["totalDocs"] == 10
            assert result["results"] == []
    
    @pytest.mark.asyncio
    async def test_create_paginate_response_without_page(self):
        mock_collection = AsyncMock()
        match = {"status": "pending"}
        results = [{"id": "1"}, {"id": "2"}]
        
        with patch('app.tools.paginate_results', return_value=(None, 0, results)) as mock_paginate:
            result = await create_paginate_response(None, mock_collection, match)
            
            assert result["page"] is None
            assert result["pageSize"] == 3
            assert result["totalPages"] == 1
            assert result["totalDocs"] == 2
            assert result["results"] == results


class TestPaginationResults:
    """Test cases for pagination results."""
    
    @pytest.mark.asyncio
    async def test_paginate_results_without_page(self):
        mock_collection = AsyncMock()
        mock_cursor = AsyncMock()
        mock_collection.find.return_value = mock_cursor
        
        sample_docs = [
            {"_id": ObjectId("507f1f77bcf86cd799439011"), "status": "pending"},
            {"_id": ObjectId("507f1f77bcf86cd799439012"), "status": "approved"}
        ]
        mock_cursor.to_list.return_value = sample_docs
        
        with patch('app.tools.convert_dict_camel_case', side_effect=lambda x: x):
            page, total_docs, result = await paginate_results(None, mock_collection, {})
            
            assert page is None
            assert total_docs == 0
            assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_paginate_results_with_page(self):
        mock_collection = AsyncMock()
        mock_collection.count_documents.return_value = 10
        
        with patch('app.tools.paginate_documents', return_value=[]) as mock_paginate_docs:
            page, total_docs, result = await paginate_results(1, mock_collection, {})
            
            assert page == 1
            assert total_docs == 10
            assert result == []


class TestBalanceCalculation:
    """Test cases for balance calculation."""
    
    @pytest.mark.asyncio
    async def test_check_available_balance(self):
        user_id = "507f1f77bcf86cd799439011"
        wallet_data = {
            "user_id": ObjectId(user_id),
            "available_balance": 100.0,
            "transactions": [
                {
                    "id": "tx1",
                    "amount": 50.0,
                    "date_available": datetime.datetime.now() - datetime.timedelta(days=1)
                },
                {
                    "id": "tx2", 
                    "amount": 25.0,
                    "date_available": datetime.datetime.now() + datetime.timedelta(days=1)
                }
            ]
        }
        
        with patch('app.tools.check_is_valid_objectId', return_value=ObjectId(user_id)), \
             patch('app.tools.wallet_collection') as mock_wallet_collection:
            
            mock_wallet_collection.find_one.return_value = wallet_data
            mock_wallet_collection.update_one.return_value = None
            
            available, pending = await check_available_balance(user_id)
            
            assert available == 150.0  # 100 + 50 (processed transaction)
            assert pending == 25.0     # pending transaction


class TestStringConversion:
    """Test cases for string conversion utilities."""
    
    @pytest.mark.asyncio
    async def test_snake_to_camel(self):
        result = await snake_to_camel("snake_case_string")
        assert result == "snakeCaseString"
        
        result = await snake_to_camel("single")
        assert result == "single"
        
        result = await snake_to_camel("multiple_word_string")
        assert result == "multipleWordString"
    
    @pytest.mark.asyncio
    async def test_convert_dict_camel_case(self):
        input_dict = {
            "user_id": "123",
            "created_at": "2024-01-01",
            "payment_date": "2024-01-15"
        }
        
        result = await convert_dict_camel_case(input_dict)
        
        expected = {
            "userId": "123",
            "createdAt": "2024-01-01",
            "paymentDate": "2024-01-15"
        }
        assert result == expected


class TestPaginateDocuments:
    """Test cases for document pagination."""
    
    @pytest.mark.asyncio
    async def test_paginate_documents_basic(self):
        mock_cursor = AsyncMock()
        sample_docs = [
            {
                "_id": ObjectId("507f1f77bcf86cd799439011"),
                "user_id": ObjectId("507f1f77bcf86cd799439012"),
                "status": "pending"
            }
        ]
        
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.to_list.return_value = sample_docs
        
        with patch('app.tools.convert_dict_camel_case', side_effect=lambda x: x):
            result = await paginate_documents(mock_cursor, skip=0, limit=10)
            
            assert len(result) == 1
            assert isinstance(result[0]["_id"], str)
            assert isinstance(result[0]["user_id"], str)
    
    @pytest.mark.asyncio
    async def test_paginate_documents_with_wallet(self):
        mock_cursor = AsyncMock()
        sample_docs = [
            {
                "_id": ObjectId("507f1f77bcf86cd799439011"),
                "status": "pending"
            }
        ]
        
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.to_list.return_value = sample_docs
        
        with patch('app.tools.convert_dict_camel_case', side_effect=lambda x: x), \
             patch('app.tools.check_available_balance', return_value=(100.0, 50.0)):
            
            result = await paginate_documents(mock_cursor, skip=0, limit=10, add_wallet=True)
            
            assert len(result) == 1
            assert result[0]["availableBalance"] == 100.0
            assert result[0]["pendingBalance"] == 50.0