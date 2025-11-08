FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    unrar-free p7zip-full p7zip-rar unzip && \
    rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install --no-cache-dir \
    pyrofork tgcrypto pymongo pyunpack patool gunicorn==20.1.0

CMD ["python3", "-m", "Unzip.main"]
