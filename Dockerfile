FROM python:3.10-slim

# Install required system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    p7zip-full unar unzip unrar-free file && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies (including uvloop)
RUN pip install --no-cache-dir \
    tgcrypto pyrofork pymongo pyunpack patool gunicorn uvloop aiofiles

# Start the bot
CMD ["python", "bot.py"]
