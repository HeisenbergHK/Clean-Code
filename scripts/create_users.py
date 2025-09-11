import os
import sys
import time

import bcrypt
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

print("🤖 Starting to add users...")

MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = os.getenv("MONGO_HOST_PORT")
MONGO_DB = os.getenv("MONGO_INITDB_DATABASE")
MONGO_USERNAME = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

# Wait for MongoDB to be ready (important for Docker startup)
max_retries = 5
retry_delay = 2

for attempt in range(max_retries):
    try:
        # Connect to MongoDB
        client = MongoClient(
            host=MONGO_HOST,
            port=27017,
            username=MONGO_USERNAME,
            password=MONGO_PASSWORD,
            authSource="admin",
        )

        # Test the connection
        client.admin.command("ping")
        print("✅ Connected to MongoDB successfully!")

        # Get the database and collection
        db = client[MONGO_DB]
        user_collection = (
            db.users_affiliate3
        )  # CHANGED: from 'users' to 'users_affiliate3'

        break  # Connection successful, break out of retry loop

    except ConnectionFailure as e:
        print(
            f"⚠️  MongoDB connection failed (attempt {attempt + 1}/{max_retries}): {e}"
        )
        if attempt < max_retries - 1:
            time.sleep(retry_delay)
        else:
            print("❌ Could not connect to MongoDB after multiple attempts. Exiting.")
            sys.exit(1)

# 1. Define our users
users_to_add = [
    {
        "email": "admin@example.com",
        "password": "adminpassword123",
        "user_type": "admin",
    },
    {
        "email": "user@example.com",
        "password": "userpassword123",
        "user_type": "user",
    },
]

# 2. Add each user to the database
for user in users_to_add:
    # Check if user already exists to avoid duplicates
    existing_user = user_collection.find_one({"email": user["email"]})
    if existing_user:
        print(f"⚠️  User {user['email']} already exists. Skipping.")
        continue

    # Hash the password before storing it
    plain_text_password = user["password"].encode("utf-8")
    hashed_password = bcrypt.hashpw(plain_text_password, bcrypt.gensalt())

    # Replace the plain text password with the secure hash
    user["password"] = hashed_password

    # Insert the user into the database
    result = user_collection.insert_one(user)
    print(
        f"✅ User {user['email']} added successfully to users_affiliate3! Database ID: {result.inserted_id}"
    )

print("🎉 All done! Users created in users_affiliate3 collection")
client.close()
