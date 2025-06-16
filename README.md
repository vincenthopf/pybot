# PyQwerty Discord Bot 🎮

A Discord bot that authentically mimics PyQwerty's writing style using AI and comprehensive message analysis.

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](docker-compose.yml)
[![Python](https://img.shields.io/badge/Python-3.11+-green?logo=python)](bot/requirements.txt)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 🌟 Features

- **🎯 Authentic Style**: Trained on 1,386 real PyQwerty messages
- **🤖 AI-Powered**: Uses OpenRouter with Google Gemini models  
- **💬 Smart Responses**: 100% response rate to mentions, natural ambient responses
- **📱 Discord Integration**: Reply system for clean conversation threading
- **🐳 Docker Ready**: Production-ready containerized deployment
- **📊 Comprehensive Analysis**: Detailed style patterns and behavioral modeling

## 🚀 Quick Start

### Option 1: Docker Deployment (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/pyqwerty-bot.git
cd pyqwerty-bot

# 2. Configure environment
cp .env.production .env
nano .env  # Add your Discord token and OpenRouter API key

# 3. Deploy with Docker
docker-compose up -d

# 4. Check logs
docker-compose logs -f pyqwerty-bot
```

### Option 2: Local Development

```bash
# 1. Setup Python environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
cd bot/
pip install -r requirements.txt

# 3. Configure environment
cp ../.env.production .env
nano .env  # Add your credentials

# 4. Run the bot
python run_bot.py
```

## ⚙️ Configuration

### Required Environment Variables

```bash
# Discord Configuration
DISCORD_BOT_TOKEN=your_bot_token_here
OPENROUTER_API_KEY=your_openrouter_key_here

# Optional (have sensible defaults)
OPENROUTER_MODEL=google/gemini-2.5-flash-preview-05-20
RATE_LIMIT_MESSAGES=30
```

### Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications/)
2. Create new application → Bot
3. Enable these **Privileged Gateway Intents**:
   - ✅ Message Content Intent
   - ✅ Server Members Intent
4. Copy bot token to `.env` file
5. Invite bot with "Read Messages" and "Read Message History" permissions

### OpenRouter Setup

1. Sign up at [OpenRouter](https://openrouter.ai/)
2. Get API key from dashboard
3. Add to `.env` file
4. The bot uses Google Gemini models (very cost-effective)

## 🎮 Bot Behavior

### Authentic PyQwerty Style
- **Brief messages**: Averages 4.8 words per response
- **Casual tone**: 73% lowercase, minimal punctuation
- **Gaming focus**: Valorant, Minecraft references
- **Slang usage**: "bro", "fr", "nah", "ur", "wtf"
- **Self-deprecating humor**: "hardstuck", "washed", "cooked"

### Response Patterns
- **100% response rate** when directly mentioned
- **25% base response rate** for ambient chat
- **Higher probability** for questions, gaming topics, mentions
- **Rate limited**: 30+ seconds between responses
- **Reply system**: Uses Discord threads instead of mentions

### Example Interactions

```
User: "@PyQwerty what's your rank?"
Bot: [REPLIES] "hardstuck gold bro"

User: "anyone down for valorant?"  
Bot: "im down but my internet is trash rn"

User: "just hit diamond!"
Bot: "fire"
```

## 📊 Style Analysis

The bot's authenticity comes from analyzing **1,386 real PyQwerty messages**:

| Metric | Value | Description |
|--------|-------|-------------|
| **Avg Message Length** | 4.8 words | Very brief responses |
| **Lowercase Usage** | 73% | Casual capitalization |
| **No Punctuation** | 92.5% | Minimal ending punctuation |
| **Emoji Usage** | 0.2% | Rarely uses emojis |
| **Gaming References** | High | Valorant, Minecraft focused |

## 🏗️ Architecture

```
📁 Project Structure
├── 🤖 bot/                    # Production bot container
│   ├── src/                   # Bot source code
│   ├── Dockerfile            # Container configuration  
│   ├── requirements.txt      # Minimal dependencies
│   └── systemprompt.md       # 7,169-char persona prompt
├── 🔧 development/           # Analysis tools (optional)
│   ├── scripts/              # Message crawler, analyzers
│   └── data/                 # Raw Discord exports
├── docker-compose.yml        # Production deployment
└── .env.production          # Environment template
```

### Core Components

- **`src/core/bot.py`**: Main Discord bot with event handling
- **`src/ai/llm_client.py`**: OpenRouter API integration
- **`src/ai/prompt_builder.py`**: Loads systemprompt.md + context
- **`src/ai/style_validator.py`**: Ensures authentic responses
- **`systemprompt.md`**: Complete PyQwerty persona (unchanged)

## 🔧 Development

### Message Analysis Tools

```bash
# Crawl Discord messages (requires bot permissions)
python development/scripts/message_crawler.py

# Analyze writing style patterns  
python development/scripts/deep_style_analyzer.py

# Extract categorized examples
python development/scripts/message_examples_extractor.py
```

### Testing

```bash
# Test bot components
python development/test_bot.py

# Test Docker build
./test_docker_build.sh
```

## 🐳 Production Deployment

### Docker Compose (Recommended)

```yaml
# docker-compose.yml
services:
  pyqwerty-bot:
    build: ./bot
    environment:
      - DISCORD_BOT_TOKEN=${DISCORD_BOT_TOKEN}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    restart: unless-stopped
    # Resource limits included
```

### Health Monitoring

```bash
# Check bot health
curl http://localhost:8080/health

# Detailed status
curl http://localhost:8080/status

# View logs
docker-compose logs -f pyqwerty-bot
```

### Resource Requirements

| Environment | Memory | CPU | Storage |
|-------------|--------|-----|---------|
| **Development** | 256MB | 0.25 cores | 100MB |
| **Production** | 512MB | 0.5 cores | 200MB |
| **Recommended VPS** | 1GB RAM | 1 vCPU | 10GB disk |

## 🛡️ Security & Privacy

- **🔐 No hardcoded secrets**: All sensitive data in environment variables
- **👤 Non-root container**: Runs as unprivileged user
- **🚫 No data persistence**: No message storage, respects privacy
- **⚡ Rate limiting**: Prevents spam and API abuse
- **🏥 Health checks**: Built-in monitoring and auto-restart

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Test thoroughly: `python development/test_bot.py`
4. Commit changes: `git commit -m 'Add amazing feature'`
5. Push to branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Bot not responding | Check Discord token & permissions |
| API errors | Verify OpenRouter key & credits |
| Import errors | Ensure all dependencies installed |
| Docker build fails | Check Docker version & permissions |

### Debug Commands

```bash
# Check bot status
docker-compose ps

# View detailed logs  
docker-compose logs --tail=100 pyqwerty-bot

# Container health
docker stats pyqwerty-bot

# Execute shell in container
docker-compose exec pyqwerty-bot /bin/bash
```

## 🎯 Roadmap

- [ ] **Multi-server support** with per-server configuration
- [ ] **Web dashboard** for bot management and analytics  
- [ ] **Voice chat integration** for gaming sessions
- [ ] **Custom trigger phrases** and response customization
- [ ] **Analytics dashboard** showing interaction patterns

## 📞 Support

- **🐛 Bug reports**: [Create an issue](https://github.com/yourusername/pyqwerty-bot/issues)
- **💡 Feature requests**: [Discussions](https://github.com/yourusername/pyqwerty-bot/discussions)
- **❓ Questions**: Check [documentation](DEPLOYMENT.md) first

---

**Built with ❤️ for authentic Discord interactions** • **Powered by AI & comprehensive style analysis** 

*PyQwerty Bot accurately replicates writing patterns from 1,386 analyzed messages using advanced AI and style validation.*