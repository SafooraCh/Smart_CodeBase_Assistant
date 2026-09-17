FROM python:3.11-slim

WORKDIR /code

# Copy requirements first so Docker can cache this layer
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir --default-timeout=300 -r requirements.txt

# Copy application code
COPY app ./app

# Create required data directories
RUN mkdir -p /code/data/uploads /code/data/db

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]