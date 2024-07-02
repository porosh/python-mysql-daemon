# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install necessary system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    supervisor \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Create a directory for logs
RUN mkdir -p /app/logs

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Supervisor configuration file
COPY supervisord.conf /etc/supervisor/supervisord.conf

# Expose the port for the web service
EXPOSE 9001

# Run Supervisor in the foreground
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]