#!/bin/bash
set -e

echo "Starting Ingenious Extensions FastAPI application..."

# Check if environment variables are set
if [ -z "$AZURE_OPENAI_API_KEY" ]; then
    echo "Warning: AZURE_OPENAI_API_KEY not set"
fi

# Test ODBC connection if Azure SQL is configured
if [ ! -z "$AZURE_SQL_CONNECTION_STRING" ]; then
    echo "Testing ODBC connection..."
    python -c "
import pyodbc
import os
try:
    conn_str = os.environ.get('AZURE_SQL_CONNECTION_STRING')
    if conn_str:
        conn = pyodbc.connect(conn_str + ';Driver={ODBC Driver 18 for SQL Server}')
        print('ODBC connection successful')
        conn.close()
    else:
        print('No Azure SQL connection string provided')
except Exception as e:
    print(f'ODBC connection failed: {e}')
    print('Continuing without Azure SQL support...')
"
fi

# Start the Ingenious REST API server using uvicorn
echo "Starting Ingenious REST API server on ${UVICORN_HOST:-0.0.0.0}:${UVICORN_PORT:-8081}"

exec uv run ingen run-rest-api-server \
    --host "${UVICORN_HOST:-0.0.0.0}" \
    --port "${UVICORN_PORT:-8081}" \
    --workers "${UVICORN_WORKERS:-4}"
