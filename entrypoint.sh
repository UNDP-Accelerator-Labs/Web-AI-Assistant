#!/bin/bash
# Start the Ollama app in the background
ollama serve &

# Wait for the Ollama app to be ready
sleep 5

# Pull the required models
ollama pull llama3.2 || echo "Failed to pull llama3.2"
ollama pull llama3.2:3b-instruct-q4_1 || echo "Failed to pull llama3.2:3b-instruct-q4_1"

# Keep the Ollama app running in the foreground
wait