#!/bin/bash

# Setup script for Ollama Docker container

echo "🐳 Setting up Ollama Docker container..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Stop any existing Ollama container
echo "🛑 Stopping any existing Ollama containers..."
docker stop ollama-agent-system 2>/dev/null || true
docker rm ollama-agent-system 2>/dev/null || true

# Build and start the container
echo "🔨 Building and starting Ollama container..."
if command -v docker-compose &> /dev/null; then
    docker-compose up -d
else
    docker compose up -d
fi

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to start..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama is ready!"
        break
    fi
    echo -n "."
    sleep 2
done

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "❌ Ollama failed to start. Check Docker logs:"
    echo "   docker logs ollama-agent-system"
    exit 1
fi

# Pull the qwen model
echo "📥 Pulling qwen model (this may take a few minutes)..."
docker exec ollama-agent-system ollama pull qwen2.5:14b-instruct-q4_K_M || {
    echo "⚠️  qwen2.5:14b-instruct-q4_K_M not available, trying alternatives..."
    docker exec ollama-agent-system ollama pull qwen:14b || {
        echo "⚠️  qwen:14b not available, trying smaller model..."
        docker exec ollama-agent-system ollama pull qwen:7b || {
            echo "❌ Failed to pull any qwen model"
            exit 1
        }
    }
}

# List available models
echo "📋 Available models:"
docker exec ollama-agent-system ollama list

echo "✅ Ollama setup complete!"
echo ""
echo "🔧 Useful commands:"
echo "   View logs:        docker logs -f ollama-agent-system"
echo "   List models:      docker exec ollama-agent-system ollama list"
echo "   Stop container:   docker stop ollama-agent-system"
echo "   Start container:  docker start ollama-agent-system"
echo "   Test API:         curl http://localhost:11434/api/tags"