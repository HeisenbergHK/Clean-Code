# Use an official Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Copy and make entrypoint script executable
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Expose FastAPI port
EXPOSE 8000

# Use entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uvicorn", "main:router", "--host", "0.0.0.0", "--port", "8000", "--reload"]