#!/bin/sh
# Copy the example config to the data folder on first run, then hand off to python as PID 1
cp /app/data/varken.example.ini /config/varken.example.ini
exec python3 /app/Varken.py
