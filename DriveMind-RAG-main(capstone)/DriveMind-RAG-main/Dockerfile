FROM python:3.11-slim

WORKDIR /app

# Install system build dependencies for grpcio and other wheels
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential libssl-dev && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, wheel
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy source code
COPY . /app

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Render injects PORT at runtime; 10000 is Render's default for Docker services
ENV PORT=10000
EXPOSE 10000

# Use shell form so $PORT is expanded at container start
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
