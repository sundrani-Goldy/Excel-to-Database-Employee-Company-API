#!/bin/bash
set -e

# Function to check if postgres is ready
postgres_ready() {
  python << END
import sys
import psycopg2
try:
    conn = psycopg2.connect(
        dbname="${DB_NAME}",
        user="${DB_USER_NAME}",
        password="${DB_PASSWORD}",
        host="${DB_HOST_NAME}",
        port="${DB_PORT}",
    )
except psycopg2.OperationalError:
    sys.exit(1)
sys.exit(0)
END
}

# Wait for PostgreSQL to become available
until postgres_ready; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - continuing"

# Apply database migrations
echo "Applying migrations"
python manage.py migrate

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000