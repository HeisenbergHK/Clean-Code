# generate_token.py
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

print(f"JWT_SECRET: {JWT_SECRET}")

def generate_token(email):
    expiration = datetime.utcnow() + timedelta(minutes=30)
    token_data = {
        "sub": email,  # This is the crucial part - must include "sub"
        "exp": expiration,
        "iat": datetime.utcnow()  # issued at time
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