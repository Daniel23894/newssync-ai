# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies for Pandas/Numpy, deletes temporary installation files
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code into working dir
COPY . .

# Expose port 8000 for FastAPI
EXPOSE 8000

# Start the FastAPI engine: server, FastAPI-instans, listen on all interfaces to allow external access
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]