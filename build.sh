#!/usr/bin/env bash
# exit on error
set -o errexit

# Install python dependencies
pip install -r requirements.txt

# Install Playwright browsers and system dependencies
# Note: In some environments, you might need to use 'pip install playwright' first
playwright install chromium
python -m playwright install-deps chromium
