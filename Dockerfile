FROM python:3.13-slim

RUN apt-get update && apt-get install -y iputils-ping && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY CIDRKnight.py .

ENTRYPOINT ["python", "CIDRKnight.py"]
