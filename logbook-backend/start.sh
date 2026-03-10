#!/bin/bash
# Ensure the data directory exists
mkdir -p /data/uploads/experiments
# Start the FastAPI application
uvicorn main:app --host 0.0.0.0 --port $PORT
