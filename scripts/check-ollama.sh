#!/bin/bash

# Health check script for Ollama
# This script checks if Ollama is running and has the required models

echo "Checking Ollama status..."

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "❌ Ollama is not running or not accessible at http://localhost:11434"
    echo "Please start Ollama with: docker-compose up ollama -d"
    exit 1
fi

echo "✅ Ollama is running"

# Check available models
echo ""
echo "Available models:"
curl -s http://localhost:11434/api/tags | jq -r '.models[].name' 2>/dev/null || echo "No models found"

# Check if the default model is available
DEFAULT_MODEL="llama2"
if curl -s http://localhost:11434/api/tags | jq -r '.models[].name' | grep -q "^$DEFAULT_MODEL"; then
    echo "✅ Default model ($DEFAULT_MODEL) is available"
else
    echo "⚠️  Default model ($DEFAULT_MODEL) is not available"
    echo "Run ./scripts/setup-ollama.sh to download models"
fi

# Test model inference
echo ""
echo "Testing model inference..."
TEST_RESPONSE=$(curl -s -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d "{\"model\": \"$DEFAULT_MODEL\", \"prompt\": \"Hello\", \"stream\": false}" \
  | jq -r '.response' 2>/dev/null)

if [ "$TEST_RESPONSE" != "null" ] && [ -n "$TEST_RESPONSE" ]; then
    echo "✅ Model inference test successful"
    echo "Sample response: $TEST_RESPONSE"
else
    echo "❌ Model inference test failed"
    echo "Please check if the model is properly loaded"
fi

echo ""
echo "Ollama health check complete!"
