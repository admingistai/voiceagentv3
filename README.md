# Voice Agent Module 🎙️

A modular, production-ready voice agent system that can extract knowledge from article URLs and engage in intelligent voice conversations. Built with LiveKit Agents framework, featuring Deepgram STT, Cartesia TTS, and OpenAI GPT models.

## Features ✨

- **📰 Article Knowledge Base**: Extract and process text from any article URL
- **🗣️ Real-time Voice Interaction**: Low-latency voice conversations with natural speech
- **🧠 Intelligent Responses**: Context-aware answers based on processed articles
- **🔧 Modular Design**: Easy to integrate into any project
- **🚀 Railway Ready**: One-click deployment to Railway platform
- **🔌 Flexible Configuration**: Support for multiple STT/TTS/LLM providers

## Quick Start 🚀

### Prerequisites

- Python 3.11+
- API Keys for:
  - LiveKit (real-time communication)
  - OpenAI (LLM processing)
  - Deepgram (speech-to-text)
  - Cartesia (text-to-speech)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/voice-agent-module.git
cd voice-agent-module
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Basic Usage

```python
from src.agent import run_agent

# List of article URLs to process
article_urls = [
    "https://example.com/article-about-ai",
    "https://example.com/article-about-technology"
]

# Run the voice agent
run_agent(article_urls)
```

## Architecture 🏗️

```
voice-agent-module/
├── src/
│   ├── agent.py              # Main voice agent implementation
│   ├── article_extractor.py  # Web scraping and text extraction
│   ├── knowledge_base.py     # Knowledge processing with OpenAI
│   └── config.py             # Configuration management
├── examples/                  # Usage examples
├── docs/                     # Additional documentation
├── Dockerfile                # Container configuration
├── railway.toml              # Railway deployment config
└── requirements.txt          # Python dependencies
```

## How It Works 🔍

1. **Article Extraction**: The system fetches and extracts clean text from provided URLs
2. **Knowledge Processing**: OpenAI processes the text to create summaries, key points, and searchable knowledge
3. **Voice Interaction**: Users speak to the agent, which processes speech through Deepgram
4. **Intelligent Response**: The agent queries its knowledge base and generates contextual responses
5. **Natural Speech**: Responses are converted to natural speech using Cartesia

## Configuration 🔧

### Environment Variables

```bash
# LiveKit Configuration
LIVEKIT_URL=wss://your-instance.livekit.cloud
LIVEKIT_API_KEY=your-livekit-api-key
LIVEKIT_API_SECRET=your-livekit-api-secret

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
LLM_MODEL=gpt-4o-mini  # Options: gpt-4o, gpt-4-turbo, gpt-3.5-turbo

# Deepgram Configuration
DEEPGRAM_API_KEY=your-deepgram-api-key
STT_MODEL=nova-3  # Options: nova-2, enhanced, base

# Cartesia Configuration
CARTESIA_API_KEY=your-cartesia-api-key
TTS_MODEL=sonic-2  # Options: sonic, aura-2
TTS_VOICE_ID=a0e99841-438c-4a64-b679-ae501e7d6091

# General Settings
LANGUAGE=en
LOG_LEVEL=INFO
```

### Programmatic Configuration

```python
from src.config import Config
from src.agent import run_agent

# Create custom configuration
config = Config(
    livekit_url="wss://your-instance.livekit.cloud",
    livekit_api_key="your-key",
    # ... other configuration
)

# Run with custom config
run_agent(article_urls, config=config)
```

## API Reference 📚

### ArticleExtractor

```python
from src.article_extractor import ArticleExtractor

extractor = ArticleExtractor(timeout=30)

# Extract single article
article = extractor.extract_from_url("https://example.com/article")

# Extract multiple articles
articles = extractor.extract_multiple(["url1", "url2"])
```

### KnowledgeBase

```python
from src.knowledge_base import KnowledgeBase

kb = KnowledgeBase(api_key="openai-key")

# Process articles
kb.add_articles(articles)

# Search knowledge
results = kb.search("artificial intelligence", top_k=3)

# Get conversation context
context = kb.get_conversation_context()
```

### VoiceAgent

```python
from src.agent import VoiceAgent, Config

config = Config.from_env()
agent = VoiceAgent(config)

# Add articles
agent.add_article_urls(["url1", "url2"])

# Prepare knowledge base
agent.prepare_knowledge_base()
```

## Deployment 🚀

### Railway Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed Railway deployment instructions.

Quick steps:
1. Fork this repository
2. Connect to Railway
3. Add environment variables
4. Deploy!

### Docker Deployment

```bash
# Build image
docker build -t voice-agent .

# Run container
docker run --env-file .env voice-agent
```

## Examples 💡

### Processing Technical Documentation

```python
# Process multiple technical articles
tech_urls = [
    "https://docs.python.org/3/tutorial/",
    "https://react.dev/learn",
    "https://kubernetes.io/docs/concepts/"
]

run_agent(tech_urls)
```

### Custom Voice Configuration

```python
config = Config.from_env()
config.tts_voice_id = "custom-voice-id"
config.tts_model = "aura-2"

run_agent(article_urls, config=config)
```

## Development 🛠️

### Running Tests

```bash
python -m pytest tests/
```

### Adding New Features

1. Create a new module in `src/`
2. Update the agent to use the new feature
3. Add tests and documentation
4. Submit a pull request

## Troubleshooting 🔍

### Common Issues

1. **Missing API Keys**: Ensure all required environment variables are set
2. **Connection Errors**: Check your LiveKit URL and credentials
3. **Extraction Failures**: Some websites may block scraping; try different articles
4. **Audio Issues**: Ensure your system has proper audio input/output devices

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python -m src.agent
```

## Contributing 🤝

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License 📄

MIT License - see [LICENSE](LICENSE) file for details

## Support 💬

- Documentation: See `/docs` folder
- Issues: GitHub Issues
- Discussions: GitHub Discussions

---

Built with ❤️ using LiveKit, Deepgram, Cartesia, and OpenAI