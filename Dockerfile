FROM python:3.10-slim

# Install system dependencies (7z, unzip, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    7zip unzip unar && \
    rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir \
    tgcrypto pyrofork pymongo pyunpack patool gunicorn

# Start the bot
CMD ["python", "bot.py"]
