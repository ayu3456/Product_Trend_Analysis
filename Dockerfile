# Use a more robust base image (Full Python instead of Slim) 
# to ensure Playwright and ML dependencies have a stable environment.
FROM python:3.9

# Set working directory
WORKDIR /app

# Set environment variables for non-interactive installs
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install essential system tools
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and then install its dependencies
# We run apt-get update again to ensure the playwright script has a fresh cache
RUN apt-get update && \
    python -m playwright install chromium && \
    python -m playwright install-deps chromium && \
    rm -rf /var/lib/apt/lists/*

# Copy the rest of the application code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
ENTRYPOINT ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
