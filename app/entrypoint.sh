#!/bin/sh
set -e

echo "Running database seed..."
python seed.py

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 --reload app:app
