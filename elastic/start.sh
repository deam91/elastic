#!/bin/sh
python3 ./manage.py collectstatic --no-input
python3 ./manage.py migrate
# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn --reload elastic.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 --timeout 60
