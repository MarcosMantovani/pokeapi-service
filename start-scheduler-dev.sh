#!/bin/bash
./wait-for-it.sh -t 0 pokeapi-service:8882 -- echo "API IS UP"
python manage.py celery_worker