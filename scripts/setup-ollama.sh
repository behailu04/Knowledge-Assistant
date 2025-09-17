#!/bin/bash

# Setup script for Ollama models
# This script pulls the required models for the Knowledge Assistant

echo "Setting up Ollama models for Knowledge Assistant..."

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "Error: Ollama is not running. Please start Ollama first."
    echo "You can start Ollama with: docker-compose up ollama -d"
    exit 1
fi

# List of models to pull
MODELS=(
    "llama2:7b"
    "llama2:13b"
    "codellama:7b"
    "mistral:7b"
    "neural-chat:7b"
)

echo "Available models:"
curl -s http://localhost:11434/api/tags | jq -r '.models[].name' 2>/dev/null || echo "No models found"

echo ""
echo "Pulling recommended models for Knowledge Assistant..."

# Pull each model
for model in "${MODELS[@]}"; do
    echo "Pulling $model..."
    curl -X POST http://localhost:11434/api/pull -d "{\"name\": \"$model\"}" &
done

# Wait for all pulls to complete
wait

echo ""
echo "Setup complete! Available models:"
curl -s http://localhost:11434/api/tags | jq -r '.models[].name' 2>/dev/null || echo "No models found"

echo ""
echo "You can now start the Knowledge Assistant with:"
echo "docker-compose up -d"
