# Voice Agent Architecture 🏗️

This document describes the architecture and data flow of the Voice Agent Module.

## System Overview

The Voice Agent Module is designed as a modular, scalable system that processes article content into a searchable knowledge base and enables real-time voice conversations about that content.

## Architecture Diagram

```mermaid
graph TB
    %% External Services
    subgraph "External APIs"
        LK[LiveKit Cloud]
        OAI[OpenAI API]
        DG[Deepgram API]
        CT[Cartesia API]
    end

    %% User Inputs
    subgraph "Inputs"
        URLs[Article URLs]
        Voice[User Voice Input]
    end

    %% Core Components
    subgraph "Voice Agent Module"
        subgraph "Knowledge Pipeline"
            AE[Article Extractor<br/>trafilatura]
            KB[Knowledge Base<br/>OpenAI Processing]
            KS[(Knowledge Store<br/>In-Memory)]
        end

        subgraph "Voice Pipeline"
            VAD[Voice Activity<br/>Detection<br/>Silero]
            STT[Speech to Text<br/>Deepgram]
            AGENT[Agent Core<br/>LiveKit Agents]
            LLM[Language Model<br/>OpenAI GPT]
            TTS[Text to Speech<br/>Cartesia]
        end

        subgraph "Configuration"
            CFG[Config Manager<br/>Environment Vars]
        end
    end

    %% Railway Platform
    subgraph "Deployment Platform"
        RW[Railway Container<br/>Docker]
    end

    %% Data Flow - Knowledge Pipeline
    URLs -->|HTTP| AE
    AE -->|Extracted Text| KB
    KB -->|Processed Knowledge| KS
    KB <-->|API Calls| OAI

    %% Data Flow - Voice Pipeline
    Voice -->|WebRTC| LK
    LK -->|Audio Stream| VAD
    VAD -->|Active Speech| STT
    STT <-->|API| DG
    STT -->|Transcript| AGENT
    AGENT -->|Query| KS
    AGENT -->|Context + Query| LLM
    LLM <-->|API| OAI
    LLM -->|Response| AGENT
    AGENT -->|Text| TTS
    TTS <-->|API| CT
    TTS -->|Audio| LK
    LK -->|WebRTC| Voice

    %% Configuration Flow
    CFG -->|API Keys| AE
    CFG -->|API Keys| KB
    CFG -->|Settings| AGENT
    CFG -->|Models| STT
    CFG -->|Models| TTS
    CFG -->|Models| LLM

    %% Deployment
    RW -->|Hosts| AGENT

    %% Styling
    classDef external fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef input fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef core fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef storage fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef deploy fill:#fce4ec,stroke:#880e4f,stroke-width:2px

    class LK,OAI,DG,CT external
    class URLs,Voice input
    class AE,KB,VAD,STT,AGENT,LLM,TTS,CFG core
    class KS storage
    class RW deploy
```

## Component Details

### 1. Article Extractor (`article_extractor.py`)

**Purpose**: Extract clean, readable text from web articles

**Key Features**:
- Uses trafilatura for robust extraction
- Handles various article formats
- Extracts metadata (title, author, date)
- Cleans and formats text for processing

**Data Flow**:
```
URL → HTTP Request → HTML → Extraction → Clean Text + Metadata
```

### 2. Knowledge Base (`knowledge_base.py`)

**Purpose**: Process raw article text into structured, searchable knowledge

**Key Features**:
- Generates article summaries
- Extracts key points and topics
- Creates conversational context
- Provides search functionality

**Processing Pipeline**:
```
Article Text → OpenAI API → {
    Summary,
    Key Points,
    Topics,
    Context
} → Knowledge Store
```

### 3. Voice Agent (`agent.py`)

**Purpose**: Orchestrate real-time voice conversations using the knowledge base

**Key Features**:
- Manages WebRTC connections via LiveKit
- Coordinates STT/TTS pipeline
- Queries knowledge base
- Generates contextual responses

**Conversation Flow**:
```
1. User speaks
2. VAD detects speech activity
3. STT converts to text
4. Agent processes query
5. LLM generates response
6. TTS converts to speech
7. Audio sent back to user
```

### 4. Configuration (`config.py`)

**Purpose**: Centralized configuration management

**Key Features**:
- Environment variable validation
- API key management
- Model selection
- Logging configuration

## Data Flow Patterns

### Knowledge Preparation Flow

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant Extractor
    participant KB
    participant OpenAI

    User->>Agent: Provide Article URLs
    Agent->>Extractor: Extract Articles
    loop For Each URL
        Extractor->>Extractor: Fetch & Parse
        Extractor-->>Agent: Article Data
    end
    Agent->>KB: Process Articles
    loop For Each Article
        KB->>OpenAI: Generate Knowledge
        OpenAI-->>KB: Structured Data
        KB->>KB: Store in Memory
    end
    KB-->>Agent: Knowledge Ready
```

### Voice Conversation Flow

```mermaid
sequenceDiagram
    participant User
    participant LiveKit
    participant Agent
    participant Deepgram
    participant OpenAI
    participant Cartesia

    User->>LiveKit: Voice Input
    LiveKit->>Agent: Audio Stream
    Agent->>Deepgram: Convert to Text
    Deepgram-->>Agent: Transcript
    Agent->>Agent: Query Knowledge Base
    Agent->>OpenAI: Generate Response
    OpenAI-->>Agent: Text Response
    Agent->>Cartesia: Convert to Speech
    Cartesia-->>Agent: Audio
    Agent->>LiveKit: Audio Stream
    LiveKit->>User: Voice Output
```

## Deployment Architecture

### Railway Deployment

```mermaid
graph LR
    subgraph "Railway Platform"
        subgraph "Container"
            APP[Voice Agent<br/>Python App]
            DEPS[Dependencies<br/>pip packages]
        end
        
        ENV[Environment<br/>Variables]
        LOGS[Logging<br/>System]
        METRICS[Metrics<br/>Collection]
    end

    subgraph "External Services"
        APIs[API Services<br/>LiveKit, OpenAI, etc.]
    end

    ENV -->|Configuration| APP
    APP -->|API Calls| APIs
    APP -->|Output| LOGS
    APP -->|Stats| METRICS
```

## Scalability Considerations

### Vertical Scaling
- Increase memory for larger knowledge bases
- More CPU for concurrent conversations
- Adjust based on article complexity

### Horizontal Scaling
- Multiple agent instances
- Load balancing via LiveKit
- Shared knowledge base (future: Redis)

### Performance Optimizations
1. **Knowledge Caching**: Store processed articles
2. **Connection Pooling**: Reuse API connections
3. **Async Processing**: Non-blocking I/O operations
4. **Batch Processing**: Multiple articles at once

## Security Architecture

### API Key Management
```
Environment Variables
    ↓
Config Module (validation)
    ↓
Service Clients (usage)
```

### Data Privacy
- No persistent storage of conversations
- Article content processed in memory
- API keys never logged
- Secure WebRTC connections

## Extension Points

### Adding New STT Providers
```python
# Easy to swap providers
stt=azure.STT(model="whisper")  # Instead of Deepgram
```

### Adding New TTS Providers
```python
# Flexible TTS selection
tts=elevenlabs.TTS(voice_id="custom")  # Instead of Cartesia
```

### Custom Knowledge Processing
```python
# Extend KnowledgeBase class
class CustomKnowledgeBase(KnowledgeBase):
    def process_article(self, article):
        # Custom processing logic
        pass
```

## Monitoring and Observability

### Logging Hierarchy
```
INFO: High-level operations
DEBUG: Detailed processing steps
WARNING: Non-critical issues
ERROR: Failures requiring attention
```

### Key Metrics
- Article extraction success rate
- Knowledge processing time
- STT/TTS latency
- API call counts
- Memory usage

## Future Architecture Enhancements

### Phase 1: Persistence
- Add database for knowledge storage
- Implement article caching
- Session management

### Phase 2: Advanced Features
- Multi-language support
- Real-time article updates
- Voice customization
- Emotion detection

### Phase 3: Scale
- Distributed knowledge base
- Multi-region deployment
- WebSocket clustering
- Advanced caching strategies

---

This architecture provides a solid foundation for a production-ready voice agent system while maintaining flexibility for future enhancements.