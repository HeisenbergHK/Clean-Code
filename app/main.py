from datetime import datetime
from typing import Optional

from fastapi import Depends, FastAPI

from app.database import payout_collection
from app.JWT_authentication import AuthenticationFactory
from app.tools import create_paginate_response

# Create authentication service instances
auth_service = AuthenticationFactory.create_authentication_service()
query_processor = AuthenticationFactory.create_query_processor()

router = FastAPI()


@router.get("/payout")
async def all_payout(
    statuses: Optional[str] = None,
    page: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_type: Optional[str] = None,
    payment_start_date: Optional[datetime] = None,
    payment_end_date: Optional[datetime] = None,
    admin: str = Depends(auth_service.check_user_is_admin),
):
    """
    Retrieve paginated payout records with optional filtering.

    Args:
        statuses: Comma-separated status values to filter by
        page: Page number for pagination
        start_date: Filter records created after this date
        end_date: Filter records created before this date
        user_type: Filter by user type
        payment_start_date: Filter by payment date after this date
        payment_end_date: Filter by payment date before this date
        admin: Admin authentication (automatically injected via dependency)

    Returns:
        Paginated response containing payout records
    """
    # Initialize match dictionary with nested date filters
    match = {"created": {}, "payment_date": {}}

    # Apply date filters for creation date
    if start_date:
        match["created"]["$gte"] = start_date
    if end_date:
        match["created"]["$lte"] = end_date

    # Apply date filters for payment date
    if payment_start_date:
        match["payment_date"]["$gte"] = payment_start_date
    if payment_end_date:
        match["payment_date"]["$lte"] = payment_end_date

    # Clean up empty date filters
    if len(match["created"]) == 0:
        del match["created"]
    if len(match["payment_date"]) == 0:
        del match["payment_date"]

    # Apply user type filter if provided
    if user_type:
        match["user_type"] = user_type

    # Apply status filter if provided
    if statuses:
        status_list = await query_processor.get_status_list_from_query(statuses)
        match["status"] = {"$in": status_list}

    # Return paginated results
    return await create_paginate_response(page, payout_collection, match)
