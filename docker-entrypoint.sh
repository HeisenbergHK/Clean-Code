#!/bin/bash

# Wait for MongoDB to be ready and create users
python scripts/create_users.py

# Start the main application
exec "$@"