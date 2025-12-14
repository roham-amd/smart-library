# Use Python 3.11 slim image
FROM python:3.14.2-alpine3.23

# Set working directory
WORKDIR /app

# Copy the Python script
COPY main.py .

# Run the application
CMD ["python", "main.py"]