FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    unrar-free p7zip-full unzip && \
    rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir \
    tgcrypto pyrofork pymongo pyunpack patool gunicorn

# Start the bot
CMD ["python", "main.py"]
