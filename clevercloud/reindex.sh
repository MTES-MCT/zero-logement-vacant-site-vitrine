#!/bin/bash -l

cd "${APP_HOME}"
uv run python manage.py update_index
