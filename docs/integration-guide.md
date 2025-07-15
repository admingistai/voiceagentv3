# Integration Guide: Using Your Railway Voice Agent

This guide shows how to integrate your deployed Railway voice agent into other projects and applications.

## 🌐 Railway Deployment Overview

When you deploy to Railway, your voice agent becomes accessible in several ways:

### 1. **LiveKit Room Integration** (Recommended)
Your deployed agent listens for LiveKit room connections. Other apps connect to the same LiveKit instance.

### 2. **HTTP API Integration** 
Use the agent's knowledge base and processing capabilities via HTTP endpoints.

### 3. **Package Integration**
Use the voice agent as a Python package in other Python projects.

---

## 🚀 Method 1: LiveKit Room Integration

This is the primary way to use your voice agent. Other applications connect to the same LiveKit room.

### Web Application Integration

```html
<!-- Frontend: Connect to the same LiveKit room -->
<!DOCTYPE html>
<html>
<head>
    <script src="https://unpkg.com/@livekit/components-js@0.2.3/dist/livekit-components.js"></script>
</head>
<body>
    <div id="room-container">
        <lk-audio-conference></lk-audio-conference>
    </div>
    
    <script>
        const roomUrl = 'wss://your-instance.livekit.cloud';
        const token = 'your-room-token'; // Generate with LiveKit API
        
        // Connect to the same room as your agent
        const room = new LiveKit.Room();
        room.connect(roomUrl, token);
        
        // Your voice agent will automatically join and respond
    </script>
</body>
</html>
```

### Mobile App Integration (React Native)

```javascript
// React Native: Connect to agent's room
import { LiveKitRoom } from '@livekit/react-native';

function VoiceAgentChat() {
  const roomUrl = 'wss://your-instance.livekit.cloud';
  const token = generateRoomToken(); // Your token generation logic
  
  return (
    <LiveKitRoom
      serverUrl={roomUrl}
      token={token}
      onConnected={(room) => {
        console.log('Connected to voice agent room');
        // Agent will respond to speech automatically
      }}
    >
      {/* Your UI components */}
    </LiveKitRoom>
  );
}
```

### Backend Integration (Node.js)

```javascript
// Node.js: Programmatically connect to agent
const { Room } = require('livekit-client');

async function connectToVoiceAgent(articleUrls) {
  const room = new Room();
  
  await room.connect('wss://your-instance.livekit.cloud', token);
  
  // Send data to the agent (if you've added data tracks)
  const dataTrack = await room.localParticipant.publishData(
    JSON.stringify({ articles: articleUrls }),
    'reliable'
  );
  
  // Listen for agent responses
  room.on('dataReceived', (payload, participant) => {
    if (participant.identity === 'voice-agent') {
      const response = JSON.parse(payload);
      console.log('Agent response:', response);
    }
  });
}
```

---

## 🌐 Method 2: HTTP API Integration

Add HTTP endpoints to your voice agent for external integrations.

### Add to your agent.py:

```python
# src/agent.py - Add HTTP server capability
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import threading

app = FastAPI(title="Voice Agent API")

class ArticleRequest(BaseModel):
    urls: List[str]
    query: Optional[str] = None

class KnowledgeQuery(BaseModel):
    question: str
    top_k: int = 3

# Global knowledge base instance
global_kb = None

@app.post("/process-articles")
async def process_articles(request: ArticleRequest):
    """Process articles and add to knowledge base"""
    global global_kb
    
    try:
        # Extract articles
        extractor = ArticleExtractor()
        articles = []
        
        for url in request.urls:
            article = extractor.extract_from_url(url)
            if article:
                articles.append(article)
        
        # Add to knowledge base
        if global_kb:
            global_kb.add_articles(articles)
            
        return {
            "success": True,
            "processed": len(articles),
            "message": f"Added {len(articles)} articles to knowledge base"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query-knowledge")
async def query_knowledge(request: KnowledgeQuery):
    """Query the knowledge base"""
    global global_kb
    
    if not global_kb:
        raise HTTPException(status_code=400, detail="Knowledge base not initialized")
    
    try:
        results = global_kb.search(request.question, top_k=request.top_k)
        context = global_kb.get_conversation_context()
        
        return {
            "question": request.question,
            "results": results,
            "context": context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "voice-agent"}

def start_http_server(port: int = 8080):
    """Start HTTP server in background thread"""
    uvicorn.run(app, host="0.0.0.0", port=port)

# Modify your main run_agent function:
def run_agent(article_urls: List[str], config: Config = None):
    """Enhanced run_agent with HTTP API"""
    global global_kb
    
    # ... existing code ...
    
    # Start HTTP server in background
    http_thread = threading.Thread(
        target=start_http_server,
        args=(config.port if config else 8080,),
        daemon=True
    )
    http_thread.start()
    
    # Store knowledge base globally for API access
    global_kb = knowledge_base
    
    # ... rest of existing LiveKit agent code ...
```

### Update requirements.txt:

```txt
# Add to requirements.txt
fastapi>=0.104.0
uvicorn>=0.24.0
```

### Using the HTTP API from other projects:

```python
# Other Python project
import requests

# Process articles
response = requests.post(
    'https://your-railway-app.railway.app/process-articles',
    json={'urls': ['https://example.com/article1']}
)

# Query knowledge
response = requests.post(
    'https://your-railway-app.railway.app/query-knowledge',
    json={'question': 'What are the main points?'}
)
print(response.json())
```

```javascript
// JavaScript/Node.js project
const axios = require('axios');

const baseURL = 'https://your-railway-app.railway.app';

// Process articles
await axios.post(`${baseURL}/process-articles`, {
  urls: ['https://example.com/article1']
});

// Query knowledge  
const response = await axios.post(`${baseURL}/query-knowledge`, {
  question: 'What are the main topics?'
});

console.log(response.data);
```

---

## 📦 Method 3: Package Integration

Use your voice agent as a Python package in other projects.

### Install as Package

```bash
# In other Python project
pip install git+https://github.com/admingistai/voiceagentv3.git
```

### Import and Use

```python
# other_project/main.py
from voice_agent_module.src.article_extractor import ArticleExtractor
from voice_agent_module.src.knowledge_base import KnowledgeBase
from voice_agent_module.src.config import Config

def my_application():
    # Use components directly
    config = Config.from_env()
    
    # Extract articles
    extractor = ArticleExtractor()
    articles = extractor.extract_multiple([
        'https://example.com/article1',
        'https://example.com/article2'
    ])
    
    # Build knowledge base
    kb = KnowledgeBase(api_key=config.openai_api_key)
    kb.add_articles(articles)
    
    # Query knowledge
    results = kb.search("What are the key insights?")
    
    return results
```

---

## 🔗 Integration Patterns

### Pattern 1: Article Processing Pipeline

```python
# Integration in content management system
class ContentProcessor:
    def __init__(self, voice_agent_url):
        self.agent_url = voice_agent_url
    
    async def process_new_article(self, url):
        # Send to voice agent for processing
        response = await self.send_to_agent([url])
        
        # Store processed knowledge
        await self.store_knowledge(response)
        
        # Notify users that agent has new knowledge
        await self.notify_agent_updated()
    
    async def send_to_agent(self, urls):
        async with aiohttp.ClientSession() as session:
            return await session.post(
                f"{self.agent_url}/process-articles",
                json={"urls": urls}
            )
```

### Pattern 2: Chatbot Integration

```python
# Integration in existing chatbot
class EnhancedChatbot:
    def __init__(self, voice_agent_api):
        self.voice_agent = voice_agent_api
        self.fallback_enabled = True
    
    async def handle_message(self, user_message):
        # Try to answer with local knowledge first
        local_response = self.get_local_response(user_message)
        
        if not local_response and self.fallback_enabled:
            # Fallback to voice agent knowledge base
            agent_response = await self.query_voice_agent(user_message)
            return agent_response
        
        return local_response
    
    async def query_voice_agent(self, question):
        response = await requests.post(
            f"{self.voice_agent}/query-knowledge",
            json={"question": question}
        )
        return response.json()
```

### Pattern 3: Real-time Collaboration

```python
# Integration in collaboration platform
class CollaborationRoom:
    def __init__(self, livekit_config):
        self.room = LiveKitRoom(livekit_config)
        self.voice_agent_connected = False
    
    async def start_voice_session(self, article_context):
        # Connect to LiveKit room
        await self.room.connect()
        
        # Send article context to voice agent
        await self.room.send_data({
            "type": "article_context",
            "articles": article_context
        })
        
        # Voice agent will process and be ready for conversation
        self.voice_agent_connected = True
    
    async def ask_agent(self, question):
        if self.voice_agent_connected:
            # Send voice or text to agent
            await self.room.send_audio(question)
```

---

## 🛠️ Development Workflow

### Local Development with Remote Agent

```bash
# 1. Keep agent running on Railway
# 2. Connect local development to Railway agent

# Local .env
LIVEKIT_URL=wss://your-instance.livekit.cloud  # Same as Railway
VOICE_AGENT_API=https://your-railway-app.railway.app
```

### Testing Integration

```python
# test_integration.py
import pytest
import asyncio
from your_app import integrate_with_voice_agent

@pytest.mark.asyncio
async def test_voice_agent_integration():
    # Test article processing
    result = await integrate_with_voice_agent([
        "https://example.com/test-article"
    ])
    
    assert result["success"] == True
    assert result["processed"] > 0

@pytest.mark.asyncio  
async def test_knowledge_query():
    # Test knowledge querying
    response = await query_voice_agent("What is this about?")
    
    assert "results" in response
    assert len(response["results"]) > 0
```

---

## 🚀 Production Considerations

### Environment Variables
```bash
# In your other project's .env
VOICE_AGENT_URL=https://your-railway-app.railway.app
LIVEKIT_URL=wss://your-instance.livekit.cloud
LIVEKIT_API_KEY=your-key
LIVEKIT_API_SECRET=your-secret
```

### Error Handling
```python
# Robust integration with fallbacks
class VoiceAgentClient:
    def __init__(self, agent_url, timeout=30):
        self.agent_url = agent_url
        self.timeout = timeout
        self.retry_count = 3
    
    async def process_articles(self, urls):
        for attempt in range(self.retry_count):
            try:
                response = await self._make_request(
                    "/process-articles", 
                    {"urls": urls}
                )
                return response
            except Exception as e:
                if attempt == self.retry_count - 1:
                    logger.error(f"Failed to process articles: {e}")
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### Monitoring
```python
# Add monitoring to your integration
import logging

logger = logging.getLogger(__name__)

class MonitoredVoiceAgentClient:
    async def query_knowledge(self, question):
        start_time = time.time()
        
        try:
            response = await self._query(question)
            duration = time.time() - start_time
            
            logger.info(f"Voice agent query successful: {duration:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Voice agent query failed: {e}")
            raise
```

---

## 📋 Summary

Your Railway-deployed voice agent can be integrated into other projects through:

1. **LiveKit Room Connections** - For real-time voice interactions
2. **HTTP API** - For programmatic access to knowledge processing  
3. **Python Package** - For direct component usage

Choose the integration method based on your needs:
- **Real-time voice** → LiveKit integration
- **Knowledge processing** → HTTP API
- **Component reuse** → Package integration

The agent is designed to be modular and can scale to support multiple concurrent integrations! 🚀