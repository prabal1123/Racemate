#!/usr/bin/env bash
set -e
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE="racemate.settings"
python manage.py collectstatic --noinput
