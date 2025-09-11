# generate_token.py
import os
from datetime import datetime, timedelta

import jwt
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")


def generate_token(email):
    token_data = {
        "sub": email,
    }
    token = jwt.encode(token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


# Generate token for admin user
admin_token = generate_token("admin@example.com")
print(f"Admin Token: {admin_token}")

# Test decode it right away to verify
try:
    decoded = jwt.decode(admin_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    print(f"Decoded token: {decoded}")
    print(f"Email from sub: {decoded.get('sub')}")
except Exception as e:
    print(f"Decode error: {e}")
