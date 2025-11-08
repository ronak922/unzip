FROM python:3.10-slim

# Install archive tools that exist in Debian 13+
RUN apt-get update && apt-get install -y --no-install-recommends \
    p7zip-full p7zip unar unzip unrar-free file && \
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
