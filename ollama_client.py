import os
from ollama import Client

# Get the Ollama host from the environment variable or default to localhost
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')

# Initialize the Ollama client
ollama_client = Client(host=OLLAMA_HOST)  # Use 'host' instead of 'base_url'