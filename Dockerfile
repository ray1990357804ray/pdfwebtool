# Use official slim Python image
FROM python:3.11-slim

# Install Ghostscript
RUN apt-get update && apt-get install -y ghostscript

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . .

# Expose the port
EXPOSE 5000

# Start the Flask app
CMD ["python", "app.py"]
