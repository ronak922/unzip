FROM python:3.10-slim

# Install required system dependencies (7z, rar, unzip)
RUN apt-get update && apt-get install -y --no-install-recommends \
    p7zip-full p7zip-rar unrar unzip && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir \
    tgcrypto pyrofork pymongo pyunpack patool gunicorn

# Start the bot
CMD ["python", "bot.py"]
