FROM python:alpine3.18

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Flask port
EXPOSE 5000

# Environment variables with defaults (override with -e or docker-compose)
ENV MONGO_HOST=localhost \
    MONGO_PORT=27017 \
    MONGO_USERNAME=admin \
    MONGO_PASSWORD=password123 \
    MONGO_AUTH_SOURCE=admin \
    MONGO_DB_NAME=flask_app \
    MONGO_COLLECTION_NAME=users

# Run the Flask application
CMD ["python", "app.py"]