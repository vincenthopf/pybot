# PyQwerty Bot - Docker Deployment Guide

## 📦 **Project Structure**

```
py2.0/
├── bot/                          # 🤖 Production bot (Docker)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/                      # Bot source code
│   ├── systemprompt.md          # Core persona
│   ├── run_bot.py               # Entry point
│   └── data/processed/          # Style profiles
├── docker-compose.yml           # 🐳 Deployment config
├── .env.production             # 🔐 Production environment
├── scripts/                    # 🔧 Development tools
├── data/raw/                   # 📊 Crawled data (dev only)
└── README.md                   # 📖 Full documentation
```

## 🚀 **Quick Deployment**

### 1. **Setup Environment**
```bash
# Copy production environment template
cp .env.production .env

# Edit with your credentials
nano .env
```

### 2. **Required Environment Variables**
```bash
# Discord Bot Token (Required)
DISCORD_BOT_TOKEN=your_bot_token_here

# OpenRouter API Key (Required)  
OPENROUTER_API_KEY=your_openrouter_key_here

# Optional (have defaults)
TARGET_USER_ID=707614458826194955
OPENROUTER_MODEL=google/gemini-2.5-flash-preview-05-20
RATE_LIMIT_MESSAGES=30
```

### 3. **Deploy with Docker Compose**
```bash
# Build and start the bot
docker-compose up -d

# View logs
docker-compose logs -f pyqwerty-bot

# Check status
docker-compose ps
```

## 🔧 **Management Commands**

### **Basic Operations:**
```bash
# Start bot
docker-compose up -d

# Stop bot
docker-compose down

# Restart bot  
docker-compose restart pyqwerty-bot

# View real-time logs
docker-compose logs -f pyqwerty-bot

# Check bot health
curl http://localhost:8080/health
curl http://localhost:8080/status
```

### **Updates:**
```bash
# Rebuild after code changes
docker-compose build pyqwerty-bot

# Deploy updated version
docker-compose up -d --force-recreate pyqwerty-bot
```

### **Troubleshooting:**
```bash
# Execute shell in container
docker-compose exec pyqwerty-bot /bin/bash

# View detailed logs
docker-compose logs --tail=100 pyqwerty-bot

# Check resource usage
docker stats pyqwerty-bot
```

## 🏥 **Health Monitoring**

### **Health Check Endpoints:**
- `GET /health` - Basic health status
- `GET /status` - Detailed bot status

### **Example Response:**
```json
{
  "status": "running",
  "service": "pyqwerty-discord-bot", 
  "version": "1.0.0",
  "bot_connected": true,
  "bot_active": true,
  "bot_user": {
    "id": 123456789,
    "name": "PyQwerty"
  }
}
```

## 🔐 **Security Considerations**

### **Environment Variables:**
- ✅ Use `.env` file for secrets
- ✅ Never commit tokens to git
- ✅ Use production environment template

### **Container Security:**
- ✅ Runs as non-root user (`botuser`)
- ✅ Resource limits configured
- ✅ Isolated network
- ✅ Minimal image footprint

### **Network Security:**
```bash
# Health endpoint is optional
# Comment out ports in docker-compose.yml if not needed
# ports:
#   - "8080:8080"
```

## 📊 **Resource Requirements**

### **Minimum System Requirements:**
- **Memory**: 256MB (512MB limit)
- **CPU**: 0.25 cores (0.5 core limit)  
- **Storage**: 100MB
- **Network**: Stable internet connection

### **Recommended Server Specs:**
- **VPS**: 1GB RAM, 1 CPU core
- **Cloud**: AWS t3.micro, GCP e2-micro
- **Self-hosted**: Raspberry Pi 4+ or similar

## 🔄 **Production Deployment**

### **Server Setup:**
```bash
# On your server
git clone <repository>
cd py2.0

# Setup environment
cp .env.production .env
nano .env  # Add your tokens

# Install Docker & Docker Compose
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Deploy
docker-compose up -d

# Enable auto-restart
sudo systemctl enable docker
```

### **Systemd Service (Optional):**
```bash
# Create service file
sudo nano /etc/systemd/system/pyqwerty-bot.service

[Unit]
Description=PyQwerty Discord Bot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
WorkingDirectory=/path/to/py2.0

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable pyqwerty-bot
sudo systemctl start pyqwerty-bot
```

## 📝 **Environment Variables Reference**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DISCORD_BOT_TOKEN` | ✅ | - | Discord bot token |
| `OPENROUTER_API_KEY` | ✅ | - | OpenRouter API key |
| `TARGET_USER_ID` | ❌ | 707614458826194955 | Original user ID |
| `TARGET_USERNAME` | ❌ | pyqwerty123 | Original username |
| `OPENROUTER_MODEL` | ❌ | google/gemini-2.5-flash-preview-05-20 | LLM model |
| `OPENROUTER_MAX_TOKENS` | ❌ | 150 | Max response tokens |
| `OPENROUTER_TEMPERATURE` | ❌ | 0.8 | Response creativity |
| `RATE_LIMIT_MESSAGES` | ❌ | 30 | Seconds between responses |
| `LOG_LEVEL` | ❌ | INFO | Logging verbosity |

## 🐛 **Common Issues**

### **Bot Not Responding:**
1. Check Discord bot token: `docker-compose logs pyqwerty-bot`
2. Verify bot permissions in Discord server
3. Check OpenRouter API key and credits
4. Ensure message content intent is enabled

### **Memory Issues:**
```bash
# Check memory usage
docker stats pyqwerty-bot

# Increase memory limit in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 1G
```

### **API Rate Limits:**
- OpenRouter has generous limits for Gemini models
- Bot has built-in rate limiting (30s between responses)
- Check API usage in OpenRouter dashboard

## 📈 **Monitoring & Logging**

### **Log Levels:**
- `ERROR`: Critical issues only
- `INFO`: Normal operation (recommended)
- `DEBUG`: Verbose logging for troubleshooting

### **Log Rotation:**
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"    # 10MB per file
    max-file: "3"      # Keep 3 files
```

### **Metrics Collection:**
```bash
# Basic metrics
docker stats pyqwerty-bot --no-stream

# Health check monitoring
curl -f http://localhost:8080/health || echo "Bot unhealthy"
```

## 🎯 **Production Checklist**

- [ ] Discord bot token configured
- [ ] OpenRouter API key configured  
- [ ] Bot invited to Discord server with proper permissions
- [ ] Message Content Intent enabled in Discord Developer Portal
- [ ] Docker and Docker Compose installed
- [ ] Environment variables set in `.env`
- [ ] Resource limits appropriate for server
- [ ] Health checks responding
- [ ] Logs showing successful startup
- [ ] Bot responding to test mentions

## 🆘 **Support**

For issues:
1. Check logs: `docker-compose logs pyqwerty-bot`
2. Verify health: `curl http://localhost:8080/health`
3. Test Discord permissions
4. Validate environment variables

The bot is designed to be robust and self-healing with automatic restarts and comprehensive error handling! 🚀