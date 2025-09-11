# Pagination and utility functions for MongoDB operations

DEFAULT_PAGE_SIZE = 3  # Default number of items per page
import datetime
from typing import List

from bson.objectid import ObjectId
from fastapi import HTTPException

from app.database import wallet_collection


async def check_is_valid_objectId(id: str) -> ObjectId:
    """Validate if the provided ID is a valid MongoDB ObjectId.

    Args:
        id: String to validate as ObjectId

    Returns:
        ObjectId instance if valid

    Raises:
        HTTPException: 400 error if ID is invalid
    """
    try:
        return ObjectId(id)
    except:
        raise HTTPException(detail="not valid object id", status_code=400)


async def create_paginate_response(
    page: int, collection, match: dict, add_wallet: bool = False
) -> dict:
    """Create a standardized pagination response.

    Args:
        page: Current page number (None returns all results)
        collection: MongoDB collection to query
        match: MongoDB query filter
        add_wallet: Whether to include wallet balance info

    Returns:
        Dictionary with pagination metadata and results
    """
    page, total_docs, result = await paginate_results(
        page, collection, match, add_wallet
    )
    return {
        "page": page,
        "pageSize": DEFAULT_PAGE_SIZE,
        "totalPages": -(-total_docs // DEFAULT_PAGE_SIZE) if page else 1,
        "totalDocs": total_docs if page else len(result),
        "results": result,
    }


async def paginate_results(
    page: int, collection, match: dict, add_wallet: bool = False
) -> tuple:
    """Paginate results from MongoDB collection.

    Args:
        page: Page number (None returns all results)
        collection: MongoDB collection to query
        match: MongoDB query filter
        add_wallet: Whether to include wallet balance info

    Returns:
        Tuple of (page, total_docs, results)
    """
    total_docs = 0
    if page is None:
        # Return all results without pagination
        cursor = collection.find(match)
        result = await cursor.to_list(length=None)

        for index, doc in enumerate(result):
            doc["_id"] = str(doc["_id"])
            if "affiliate_tracking_id" in doc:
                doc["affiliate_tracking_id"] = str(doc["affiliate_tracking_id"])
            if "user_id" in doc:
                doc["user_id"] = str(doc["user_id"])

            if add_wallet:
                available_balance, pending_balance = await check_available_balance(
                    doc["_id"]
                )
                doc["available_balance"] = available_balance
                doc["pending_balance"] = pending_balance

            result[index] = await convert_dict_camel_case(doc)
    else:
        # Return paginated results
        total_docs = await collection.count_documents(match)
        if page < 1:
            page = 1

        skip = (page - 1) * DEFAULT_PAGE_SIZE
        limit = DEFAULT_PAGE_SIZE

        cursor = collection.find(match)
        result = await paginate_documents(cursor, skip, limit, add_wallet)
    return page, total_docs, result


async def check_available_balance(user_id: str) -> tuple:
    """Calculate available and pending balance for a user.

    Args:
        user_id: User ID to check balance for

    Returns:
        Tuple of (available_balance, pending_balance)
    """
    user_id = await check_is_valid_objectId(user_id)

    wallet = await wallet_collection.find_one({"user_id": user_id})

    # Calculate the available and pending balance
    available_balance = wallet["available_balance"]
    pending_balance = 0
    transactions_to_delete = []
    for transaction in wallet["transactions"]:
        if transaction["date_available"] <= datetime.datetime.now():
            available_balance += transaction["amount"]
            transactions_to_delete.append(transaction["id"])
        else:
            pending_balance += transaction["amount"]

    # Update wallet with new balances and remove processed transactions
    await wallet_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "available_balance": available_balance,
                "pending_balance": pending_balance,
            },
            "$pull": {"transactions": {"id": {"$in": transactions_to_delete}}},
        },
    )
    return available_balance, pending_balance


async def snake_to_camel(snake_str: str) -> str:
    """Convert snake_case string to camelCase.

    Args:
        snake_str: Snake_case string to convert

    Returns:
        camelCase version of input string
    """
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


async def convert_dict_camel_case(data: dict) -> dict:
    """Convert all keys in dictionary from snake_case to camelCase.

    Args:
        data: Dictionary with snake_case keys

    Returns:
        Dictionary with camelCase keys
    """
    camel_dict = {}
    for key, value in data.items():
        camel_key = await snake_to_camel(key)
        camel_dict[camel_key] = value
    return camel_dict


async def paginate_documents(
    cursor, skip: int = 0, limit: int = 10, add_wallet: bool = False
) -> List[dict]:
    """Paginate MongoDB cursor results.

    Args:
        cursor: MongoDB cursor
        skip: Number of documents to skip
        limit: Maximum number of documents to return
        add_wallet: Whether to include wallet balance info

    Returns:
        List of processed documents
    """
    cursor = cursor.skip(skip).limit(limit)
    result = await cursor.to_list(length=limit)

    for index, doc in enumerate(result):
        _id = doc["_id"]
        doc["_id"] = str(doc["_id"])
        if "affiliate_tracking_id" in doc:
            doc["affiliate_tracking_id"] = str(doc["affiliate_tracking_id"])
        if "user_id" in doc:
            doc["user_id"] = str(doc["user_id"])

        doc = await convert_dict_camel_case(doc)
        if add_wallet:
            print(add_wallet)
            available_balance, pending_balance = await check_available_balance(_id)
            doc["availableBalance"] = available_balance
            doc["pendingBalance"] = pending_balance
        result[index] = doc
    return result
