# Railway Deployment Guide 🚂

This guide provides step-by-step instructions for deploying the Voice Agent Module to Railway.

## Prerequisites 📋

Before deploying, ensure you have:

1. A [Railway account](https://railway.app) (free tier available)
2. API keys for all required services:
   - LiveKit
   - OpenAI
   - Deepgram
   - Cartesia
3. Article URLs you want to process

## Deployment Methods 🚀

### Method 1: Deploy from GitHub (Recommended)

#### Step 1: Fork the Repository

1. Fork this repository to your GitHub account
2. Clone your fork locally:
```bash
git clone https://github.com/yourusername/voice-agent-module.git
cd voice-agent-module
```

#### Step 2: Create Railway Project

1. Log in to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your forked repository
5. Railway will automatically detect the Dockerfile

#### Step 3: Configure Environment Variables

In the Railway dashboard:

1. Click on your service
2. Go to "Variables" tab
3. Add the following variables:

```bash
# Required API Keys
LIVEKIT_URL=wss://your-instance.livekit.cloud
LIVEKIT_API_KEY=your-livekit-api-key
LIVEKIT_API_SECRET=your-livekit-api-secret
OPENAI_API_KEY=your-openai-api-key
DEEPGRAM_API_KEY=your-deepgram-api-key
CARTESIA_API_KEY=your-cartesia-api-key

# Article URLs (comma-separated)
ARTICLE_URLS=https://example.com/article1,https://example.com/article2

# Optional Configuration
LLM_MODEL=gpt-4o-mini
STT_MODEL=nova-3
TTS_MODEL=sonic-2
TTS_VOICE_ID=a0e99841-438c-4a64-b679-ae501e7d6091
LANGUAGE=en
LOG_LEVEL=INFO
```

#### Step 4: Deploy

1. Railway will automatically deploy after adding variables
2. Monitor the build logs in the dashboard
3. Once deployed, check the service logs

### Method 2: Deploy with Railway CLI

#### Step 1: Install Railway CLI

```bash
# macOS/Linux
curl -fsSL https://railway.app/install.sh | sh

# Windows (PowerShell)
iwr -useb https://railway.app/install.ps1 | iex
```

#### Step 2: Login and Initialize

```bash
# Login to Railway
railway login

# Navigate to project directory
cd voice-agent-module

# Initialize Railway project
railway init
```

#### Step 3: Configure Variables

```bash
# Set environment variables
railway variables set LIVEKIT_URL=wss://your-instance.livekit.cloud
railway variables set LIVEKIT_API_KEY=your-key
railway variables set LIVEKIT_API_SECRET=your-secret
railway variables set OPENAI_API_KEY=your-key
railway variables set DEEPGRAM_API_KEY=your-key
railway variables set CARTESIA_API_KEY=your-key
railway variables set ARTICLE_URLS=https://example.com/article1,https://example.com/article2
```

#### Step 4: Deploy

```bash
# Deploy the application
railway up
```

### Method 3: Deploy with Template

Use our Railway template for one-click deployment:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/voice-agent)

*Note: Template link would need to be created separately*

## Configuration Details 🔧

### Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `LIVEKIT_URL` | Yes | LiveKit server URL | `wss://your-instance.livekit.cloud` |
| `LIVEKIT_API_KEY` | Yes | LiveKit API key | `APIxxxxxxxxxxxxx` |
| `LIVEKIT_API_SECRET` | Yes | LiveKit API secret | `secretxxxxxxxxxx` |
| `OPENAI_API_KEY` | Yes | OpenAI API key | `sk-xxxxxxxxxxxxxxxx` |
| `DEEPGRAM_API_KEY` | Yes | Deepgram API key | `xxxxxxxxxxxxxxxx` |
| `CARTESIA_API_KEY` | Yes | Cartesia API key | `xxxxxxxxxxxxxxxx` |
| `ARTICLE_URLS` | Yes | Comma-separated article URLs | `https://site1.com,https://site2.com` |
| `LLM_MODEL` | No | OpenAI model to use | `gpt-4o-mini` |
| `STT_MODEL` | No | Deepgram model | `nova-3` |
| `TTS_MODEL` | No | Cartesia model | `sonic-2` |
| `TTS_VOICE_ID` | No | Cartesia voice ID | `a0e99841-438c-4a64-b679-ae501e7d6091` |
| `LANGUAGE` | No | Language code | `en` |
| `LOG_LEVEL` | No | Logging level | `INFO` |

### Getting API Keys

#### LiveKit
1. Sign up at [LiveKit Cloud](https://livekit.io/cloud)
2. Create a new project
3. Copy the WebSocket URL, API Key, and Secret

#### OpenAI
1. Sign up at [OpenAI Platform](https://platform.openai.com)
2. Go to API Keys section
3. Create a new API key

#### Deepgram
1. Sign up at [Deepgram](https://console.deepgram.com)
2. Create a new API key
3. Ensure "Speech-to-Text" is enabled

#### Cartesia
1. Sign up at [Cartesia](https://www.cartesia.ai)
2. Access the API dashboard
3. Generate an API key

## Monitoring and Logs 📊

### View Logs

#### Via Dashboard
1. Go to your Railway project
2. Click on the service
3. Navigate to "Logs" tab

#### Via CLI
```bash
railway logs
```

### Monitor Resources

In the Railway dashboard:
- CPU usage
- Memory consumption
- Network traffic
- Build times

## Scaling 📈

### Vertical Scaling

Adjust resources in `railway.toml`:

```toml
[services.resources]
memory = 1024  # Increase to 1GB
cpu = 1.0      # Increase to 1 full CPU
```

### Horizontal Scaling

Increase replicas:

```toml
[deploy]
numReplicas = 3  # Run 3 instances
```

## Troubleshooting 🔍

### Common Issues

#### 1. Build Failures

**Problem**: Docker build fails
**Solution**: 
- Check Dockerfile syntax
- Ensure all files are committed
- Review build logs for specific errors

#### 2. Missing Environment Variables

**Problem**: Application crashes with "Missing required environment variables"
**Solution**:
- Double-check all required variables are set
- Use Railway CLI to verify: `railway variables`

#### 3. Connection Issues

**Problem**: Cannot connect to LiveKit
**Solution**:
- Verify LiveKit URL starts with `wss://`
- Check API credentials are correct
- Ensure LiveKit instance is running

#### 4. Memory Issues

**Problem**: Service crashes with OOM (Out of Memory)
**Solution**:
- Increase memory allocation in railway.toml
- Process fewer articles at once
- Optimize code for memory usage

### Debug Mode

Enable debug logging:

1. Set `LOG_LEVEL=DEBUG` in Railway variables
2. Redeploy the service
3. Check logs for detailed information

### Health Checks

Add a health check endpoint:

```python
# In src/agent.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

Update `railway.toml`:
```toml
[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 30
```

## Advanced Configuration 🛠️

### Custom Start Command

Modify the start command in Railway dashboard:

```bash
# Process specific articles
python -m src.agent --urls "https://specific-article.com"

# Use different configuration
python -m src.agent --config production.json
```

### Environment-Specific Settings

Create multiple Railway environments:

1. Development
2. Staging  
3. Production

Each with different:
- API keys
- Model selections
- Resource allocations

### Webhook Integration

Add webhook support for dynamic article processing:

```python
# Add to src/agent.py
@app.post("/process-article")
async def process_article(url: str):
    voice_agent.add_article_urls([url])
    voice_agent.prepare_knowledge_base()
    return {"status": "processed"}
```

## Cost Optimization 💰

### Railway Pricing

- **Hobby Plan**: $5/month (includes $5 usage)
- **Pro Plan**: $20/month (includes $20 usage)

### Tips for Cost Reduction

1. **Use Sleep/Wake**:
   - Enable in Railway dashboard
   - Service sleeps when not in use

2. **Optimize Resources**:
   ```toml
   [services.resources]
   memory = 256  # Start small
   cpu = 0.25    # Quarter CPU
   ```

3. **Process Articles on Demand**:
   - Don't process all articles at startup
   - Load as needed

4. **Cache Processed Knowledge**:
   - Save knowledge base to persistent storage
   - Reload on startup

## Security Best Practices 🔒

1. **Never commit secrets**:
   - Use `.gitignore` for `.env` files
   - Always use Railway variables

2. **Rotate API keys regularly**:
   - Update in Railway dashboard
   - No code changes needed

3. **Use Railway's private networking**:
   - For multi-service architectures
   - Keeps internal traffic secure

4. **Enable 2FA**:
   - On Railway account
   - On all API provider accounts

## Support and Resources 📚

### Railway Resources
- [Railway Documentation](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)
- [Railway Status](https://status.railway.app)

### Voice Agent Resources
- [LiveKit Documentation](https://docs.livekit.io)
- [Deepgram Documentation](https://developers.deepgram.com)
- [Cartesia Documentation](https://docs.cartesia.ai)
- [OpenAI Documentation](https://platform.openai.com/docs)

### Getting Help
1. Check service logs for errors
2. Review this documentation
3. Search Railway Discord
4. Open a GitHub issue

---

Happy deploying! 🎉