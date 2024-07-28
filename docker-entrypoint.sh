#!/usr/bin/env sh

set -e

echo "Waiting for DB before running migrations."
sleep 5

# Run database migrations
python manage.py migrate --noinput

exec "$@"

# NOTE: If the first line is causing the error,
# try to change the ending style of file from CRLF to LF