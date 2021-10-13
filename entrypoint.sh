#! /bin/bash

python manage.py makemigrations --no-input

python manage.py migrate --no-input

exec gunicorn utils.wsgi:application -b 0.0.0.0:8000 --reload
