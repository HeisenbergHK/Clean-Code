import os
from typing import Any, Dict, List, Optional

import jwt
from dotenv import load_dotenv
from fastapi import Header, HTTPException

from app.database import user_collection


class ConfigManager:
    """Manages application configuration and environment variables."""

    def __init__(self):
        load_dotenv()
        self._jwt_secret = os.getenv("JWT_SECRET")
        self._jwt_algorithm = os.getenv("JWT_ALGORITHM")
        expiration_time = os.getenv("JWT_EXPIRATION_MINUTES") or "0"
        self._jwt_expiration_minutes = int(expiration_time)

    @property
    def jwt_secret(self) -> str:
        """Get JWT secret key from environment variables."""
        return self._jwt_secret

    @property
    def jwt_algorithm(self) -> str:
        """Get JWT algorithm from environment variables."""
        return self._jwt_algorithm

    @property
    def jwt_expiration_minutes(self) -> int:
        """Get JWT expiration time in minutes from environment variables."""
        return self._jwt_expiration_minutes


class JWTHandler:
    """Handles JWT token operations including decoding and validation."""

    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager

    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode and validate JWT token.

        Args:
            token: JWT token string to decode

        Returns:
            Decoded token payload as dictionary

        Note:
            Returns empty dict if token is invalid
        """
        try:
            payload = jwt.decode(
                token, self.config.jwt_secret, algorithms=[self.config.jwt_algorithm]
            )
            print(10 * "#")
            print(payload)
            return payload
        except jwt.PyJWTError as e:
            print(f"JWT Error: {str(e)}")
            print(10 * "*")
            return {}

    def extract_token_from_authorization(self, authorization: str) -> str:
        """Extract token from Authorization header.

        Args:
            authorization: Authorization header value

        Returns:
            JWT token string without 'Bearer ' prefix
        """
        if authorization.startswith("Bearer "):
            return authorization[7:]
        return authorization

    def get_email_from_token_payload(self, token_payload: Dict[str, Any]) -> str:
        """Extract email from decoded token payload.

        Args:
            token_payload: Decoded JWT token payload

        Returns:
            Email address from 'sub' claim

        Raises:
            HTTPException: 400 error if 'sub' claim is missing
        """
        if "sub" not in token_payload:
            raise HTTPException(detail="Token missing 'sub' claim", status_code=400)
        return token_payload["sub"]


class AuthenticationService:
    """Handles user authentication and authorization operations."""

    def __init__(self, jwt_handler: JWTHandler):
        self.jwt_handler = jwt_handler

    async def get_email_from_token(self, authorization: str = Header(...)) -> str:
        """Extract and validate email from JWT token.

        Args:
            authorization: Authorization header containing JWT token

        Returns:
            Email address extracted from token

        Raises:
            HTTPException: Various errors for invalid/expired tokens
        """
        try:
            token = self.jwt_handler.extract_token_from_authorization(authorization)
            decode_token = self.jwt_handler.decode_token(token)

            print(decode_token)
            print(10 * "ABABBABAB")

            email = self.jwt_handler.get_email_from_token_payload(decode_token)
            return email

        except jwt.ExpiredSignatureError:
            raise HTTPException(detail="Token expired", status_code=401)
        except jwt.InvalidTokenError as e:
            raise HTTPException(detail=f"Invalid token: {str(e)}", status_code=401)
        except Exception as e:
            print(f"Error: {str(e)}")
            raise HTTPException(detail="Invalid token", status_code=400)

    async def check_user_is_admin(
        self, authorization: str = Header(...)
    ) -> Dict[str, Any]:
        """Verify that the authenticated user has admin privileges.

        Args:
            authorization: Authorization header containing JWT token

        Returns:
            User document from database

        Raises:
            HTTPException: 404 if user not found, 400 if not admin
        """
        email = await self.get_email_from_token(authorization)

        print(10 * "#", "LOG")
        print(email)

        user = await user_collection.find_one({"email": email})

        print(10 * "#", "LOG")
        print(user)

        if user is None:
            raise HTTPException(detail="User not found", status_code=404)

        if user["user_type"] != "admin":
            raise HTTPException(detail="User is not Admin", status_code=400)

        return user


class QueryProcessor:
    """Handles query parameter processing and parsing."""

    @staticmethod
    async def get_status_list_from_query(statuses: str) -> List[str]:
        """Parse comma-separated status string into a list of statuses.

        Args:
            statuses: Comma-separated string of status values

        Returns:
            List of trimmed status strings
        """
        status_list = statuses.split(",")
        return [status.strip() for status in status_list]


class AuthenticationFactory:
    """Factory class to create and configure authentication components."""

    @staticmethod
    def create_authentication_service() -> AuthenticationService:
        """Create a fully configured authentication service.

        Returns:
            Configured AuthenticationService instance
        """
        config_manager = ConfigManager()
        jwt_handler = JWTHandler(config_manager)
        return AuthenticationService(jwt_handler)

    @staticmethod
    def create_query_processor() -> QueryProcessor:
        """Create a query processor instance.

        Returns:
            QueryProcessor instance
        """
        return QueryProcessor()
