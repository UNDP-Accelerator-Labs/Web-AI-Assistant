FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the application code
COPY . /app

# Install system dependencies required for building Python packages and Ollama
RUN apt-get update && apt-get install -y \
    build-essential \
    libhnswlib-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama CLI
RUN curl -fsSL https://ollama.com/install.sh | sh

RUN chmod +x entrypoint.sh
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the entry point to run the main.py script
CMD ["python", "main.py"]