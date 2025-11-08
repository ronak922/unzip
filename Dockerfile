FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget p7zip-full unar unzip file && \
    wget https://www.rarlab.com/rar/rarlinux-x64-621.tar.gz -O /tmp/rarlinux.tar.gz && \
    tar -xzvf /tmp/rarlinux.tar.gz -C /tmp && \
    mv /tmp/rar/rar /tmp/rar/unrar /usr/local/bin/ && \
    rm -rf /tmp/rarlinux.tar.gz /tmp/rar && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy bot files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir \
    aiofiles tgcrypto pyrofork pymongo pyunpack patool gunicorn uvloop

# Start the bot
CMD ["python", "bot.py"]
