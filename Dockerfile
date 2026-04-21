# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Create data directory
RUN mkdir -p data

# Expose port
EXPOSE 8000

# Start the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]