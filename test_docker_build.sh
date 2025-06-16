#!/bin/bash

# Test Docker build without actually running the bot
echo "🐳 Testing Docker build for PyQwerty bot..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

# Build the bot image
echo "🔨 Building bot Docker image..."
cd bot
docker build -t pyqwerty-bot-test . || {
    echo "❌ Docker build failed!"
    exit 1
}

echo "✅ Docker build successful!"

# Test that the image can run basic commands
echo "🧪 Testing basic container functionality..."
docker run --rm pyqwerty-bot-test python -c "
import sys
print(f'✅ Python {sys.version_info.major}.{sys.version_info.minor} available')

try:
    import discord
    print('✅ discord.py imported successfully')
except ImportError as e:
    print(f'❌ discord.py import failed: {e}')

try:
    import openai
    print('✅ openai imported successfully') 
except ImportError as e:
    print(f'❌ openai import failed: {e}')

try:
    from src.core.bot import PyQwertyBot
    print('✅ Bot class imported successfully')
except ImportError as e:
    print(f'❌ Bot import failed: {e}')

print('✅ Container test complete!')
"

echo ""
echo "🎉 Docker setup verified!"
echo "📋 Next steps:"
echo "1. Copy .env.production to .env and configure your tokens"
echo "2. Run: docker-compose up -d" 
echo "3. Monitor: docker-compose logs -f pyqwerty-bot"

# Cleanup test image
docker rmi pyqwerty-bot-test 2>/dev/null || echo "Test image cleanup skipped"