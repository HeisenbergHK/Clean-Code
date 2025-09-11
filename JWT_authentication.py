import os

import jwt
from dotenv import load_dotenv
from fastapi import Header, HTTPException

from database import user_collection

# Load environment variables
load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
expiration_time = os.getenv("JWT_EXPIRATION_MINUTES") or 0
JWT_EXPIRATION_MINUTES = int(expiration_time)


async def check_user_is_admin(authorization: str = Header(...)):
    email = await get_email_from_token(authorization)

    print(10*"#", "LOG")
    print(email)

    # Add 'await' here
    user = await user_collection.find_one({"email": email})

    print(10*"#", "LOG")
    print(user)
    if user is None:
        raise HTTPException(detail="User not found", status_code=404)
    if user["user_type"] != "admin":
        raise HTTPException(detail="User is not Admin", status_code=400)
    return user


async def get_email_from_token(authorization: str = Header(...)):
    try:
        # Extract token from "Bearer <token>" format
        if authorization.startswith("Bearer "):
            token = authorization[7:]
        else:
            token = authorization
            
        decode_token = decode_jwt_token(token)
        print(decode_token)
        print(10*"ABABBABAB")
        
        # Check if sub exists in the token
        if "sub" not in decode_token:
            raise HTTPException(detail="Token missing 'sub' claim", status_code=400)
            
        email = decode_token["sub"]
        return email
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(detail="Token expired", status_code=401)
    except jwt.InvalidTokenError as e:
        raise HTTPException(detail=f"Invalid token: {str(e)}", status_code=401)
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(detail="Invalid token", status_code=400)


def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        print(10*"#")
        print(payload)
        return payload
    except jwt.PyJWTError as e:
        print(f"JWT Error: {str(e)}")
        print(10*"*")
    
        return {}


async def get_status_list_from_query(statuses):
    status_list = statuses.split(",")
    lst = []
    for status in status_list:
        lst.append(status.strip())
    return lst
