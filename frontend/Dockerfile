# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory for the application
WORKDIR /app

# Copy requirements first to leverage Docker cache for faster builds
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the frontend application source code into the working directory
COPY . .

# Expose port 8501 for the Streamlit user interface
EXPOSE 8501

# Start the Streamlit app: listen on all interfaces to allow access from the host
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]