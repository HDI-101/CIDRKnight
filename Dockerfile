FROM python:3.11-slim

WORKDIR /app

COPY CIDRKnight.py .

ENTRYPOINT ["python", "CIDRKnight.py"]
