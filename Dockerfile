# Use Python 3.11 slim image as base
# This provides a good balance between size and compatibility
FROM python:3.11-slim

# Set Python to run in unbuffered mode
# This ensures that logs are output immediately
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# These are required for some Python packages and audio processing
RUN apt-get update && apt-get install -y \
    # Build essentials for compiling Python packages
    build-essential \
    # Git for potential package installations
    git \
    # Audio libraries for voice processing
    portaudio19-dev \
    # Clean up apt cache to reduce image size
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first
# This allows Docker to cache the dependency installation layer
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir reduces image size by not storing pip cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
# This includes all source code and configuration files
COPY . .

# Create a non-root user to run the application
# This is a security best practice
RUN useradd -m -u 1000 agent && \
    chown -R agent:agent /app

# Switch to the non-root user
USER agent

# Expose the port that the agent might use
# LiveKit agents typically don't need to expose ports directly
# but this is here for potential future use
EXPOSE 8080

# Set the entrypoint to run the agent
# This uses Python's -m flag to run the module
# The actual command will be provided by Railway or docker-compose
CMD ["python", "-m", "src.agent"]