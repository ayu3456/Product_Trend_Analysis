#!/usr/bin/env bash
# exit on error
set -o errexit

# Install python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers and system dependencies
python -m playwright install chromium
python -m playwright install-deps chromium
