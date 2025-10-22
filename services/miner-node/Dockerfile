FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY engine/ ./engine/
COPY job_worker.py .
COPY config.yaml .
COPY ipfs_utils.py .
COPY rpc_client.py .

RUN mkdir -p /var/log/tensora

ENV PYTHONUNBUFFERED=1

CMD ["python", "-u", "job_worker.py"]
