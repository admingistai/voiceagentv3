"""
Voice Agent Module

This is the main voice agent implementation using LiveKit Agents framework.
It integrates Deepgram for STT, Cartesia for TTS, and OpenAI for conversation,
with a custom knowledge base built from article URLs.

Key Features:
- Real-time voice conversations with low latency
- Context-aware responses based on article knowledge
- Custom tools for querying the knowledge base
- Flexible configuration for different providers
- Production-ready error handling and logging
"""

import logging
import os
from typing import Optional, List, Dict, Any
from livekit import agents
from livekit.agents import AgentSession, Agent, RunContext, WorkerOptions, cli, function_tool
from livekit.plugins import deepgram, cartesia, openai, silero

from .article_extractor import ArticleExtractor
from .knowledge_base import KnowledgeBase
from .config import Config

# Configure logging for this module
logger = logging.getLogger(__name__)


class VoiceAgent:
    """
    Main voice agent class that orchestrates the conversation.
    
    This class manages:
    - Article extraction and knowledge base creation
    - Voice interaction setup (STT/TTS)
    - LLM conversation with custom tools
    - Real-time voice processing
    """
    
    def __init__(self, config: Config):
        """
        Initialize the voice agent with configuration.
        
        Args:
            config: Configuration object with API keys and settings
        """
        self.config = config
        
        # Initialize components
        self.article_extractor = ArticleExtractor(timeout=30)
        self.knowledge_base = KnowledgeBase(
            api_key=config.openai_api_key,
            model=config.llm_model
        )
        
        # Store article URLs to process
        self.article_urls: List[str] = []
        
        logger.info("VoiceAgent initialized")
    
    def add_article_urls(self, urls: List[str]):
        """
        Add article URLs to be processed into the knowledge base.
        
        Args:
            urls: List of article URLs to process
        """
        self.article_urls.extend(urls)
        logger.info(f"Added {len(urls)} article URLs to process")
    
    def prepare_knowledge_base(self):
        """
        Extract articles and build the knowledge base.
        
        This method should be called before starting the agent
        to ensure the knowledge base is ready.
        """
        if not self.article_urls:
            logger.warning("No article URLs to process")
            return
        
        logger.info(f"Processing {len(self.article_urls)} articles...")
        
        # Extract articles
        articles = self.article_extractor.extract_multiple(self.article_urls)
        
        if not articles:
            logger.error("Failed to extract any articles")
            return
        
        # Process into knowledge base
        self.knowledge_base.add_articles(articles)
        
        logger.info(f"Knowledge base ready with {len(articles)} articles")
    
    def get_agent_instructions(self) -> str:
        """
        Generate instructions for the agent based on the knowledge base.
        
        Returns:
            Instruction string for the agent
        """
        base_instructions = """You are a helpful voice assistant with knowledge about specific articles.
        You can discuss the content of these articles, answer questions about them, and provide
        insights based on the information you have. 
        
        Key capabilities:
        - Answer questions about articles in my knowledge base
        - Search for specific topics across all articles
        - Get detailed information about specific subjects
        - List all articles currently available
        - IMPORTANT: Process new articles that users provide! If a user gives you a URL or asks you to analyze an article, use the add_article function to process it.
        
        Be conversational, friendly, and informative. When users mention URLs or ask you to analyze articles, 
        proactively offer to process them for them."""
        
        # Add knowledge context
        context = self.knowledge_base.get_conversation_context()
        
        return f"{base_instructions}\n\n{context}"
    
    def create_function_tools(self):
        """
        Create custom function tools for the agent.
        
        Returns:
            List of function tools the agent can use
        """
        # Tool to search the knowledge base
        @function_tool
        async def search_knowledge(
            context: RunContext,
            query: str,
        ):
            """Search the knowledge base for information about a specific topic."""
            logger.info(f"Searching knowledge base for: {query}")
            
            results = self.knowledge_base.search(query, top_k=2)
            
            if not results:
                return "I couldn't find specific information about that topic in my knowledge base."
            
            # Format results for the agent
            response = []
            for entry in results:
                title = entry['metadata'].get('title', 'Untitled')
                summary = entry['summary']
                response.append(f"From '{title}': {summary}")
            
            return "\n\n".join(response)
        
        # Tool to get detailed information
        @function_tool
        async def get_detailed_info(
            context: RunContext,
            topic: str,
        ):
            """Get detailed information about a specific topic from the knowledge base."""
            logger.info(f"Getting detailed info for: {topic}")
            
            details = self.knowledge_base.get_detailed_info(topic)
            
            if not details:
                return f"I don't have detailed information about '{topic}' in my current knowledge base."
            
            return details
        
        # Tool to list available articles
        @function_tool
        async def list_articles(
            context: RunContext,
        ):
            """List all articles currently in the knowledge base."""
            if not self.knowledge_base.knowledge_store:
                return "No articles are currently loaded in the knowledge base."
            
            articles = []
            for entry in self.knowledge_base.knowledge_store:
                title = entry['metadata'].get('title', 'Untitled')
                url = entry['metadata'].get('url', '')
                topics = ", ".join(entry['topics'][:3])  # First 3 topics
                articles.append(f"• {title} - Topics: {topics}")
            
            return "Articles in my knowledge base:\n" + "\n".join(articles)
        
        # Tool to process new articles during conversation
        @function_tool
        async def add_article(
            context: RunContext,
            url: str,
        ):
            """Process a new article URL and add it to the knowledge base.
            
            Args:
                url: The URL of the article to process and analyze
            """
            logger.info(f"Processing new article from URL: {url}")
            
            try:
                # Extract the article
                article = self.article_extractor.extract_from_url(url)
                
                if not article:
                    return f"Sorry, I couldn't extract content from that URL: {url}. Please check if the URL is accessible and contains readable text."
                
                # Process it into the knowledge base
                self.knowledge_base.add_articles([article])
                
                title = article.get('title', 'Untitled')
                word_count = article.get('word_count', 0)
                
                logger.info(f"Successfully added article: {title} ({word_count} words)")
                
                return f"Great! I've successfully processed and added the article '{title}' ({word_count} words) to my knowledge base. You can now ask me questions about it!"
                
            except Exception as e:
                logger.error(f"Error processing article from {url}: {e}")
                return f"I encountered an error while processing that article: {str(e)}. Please try a different URL or check if the article is publicly accessible."
        
        return [search_knowledge, get_detailed_info, list_articles, add_article]


# Global voice agent instance
voice_agent: Optional[VoiceAgent] = None


async def entrypoint(ctx: agents.JobContext):
    """
    Main entrypoint for the LiveKit agent.
    
    This function is called when a new agent job is created.
    It sets up the voice interaction and starts the conversation.
    """
    global voice_agent
    
    logger.info(f"Agent entrypoint called for job {ctx.job.id}")
    
    # Connect to the LiveKit room
    await ctx.connect()
    
    # Create the agent configuration
    agent = Agent(
        instructions=voice_agent.get_agent_instructions(),
        tools=voice_agent.create_function_tools(),
    )
    
    # Create the agent session with voice components
    session = AgentSession(
        vad=silero.VAD.load(),  # Voice Activity Detection
        stt=deepgram.STT(  # Speech-to-Text
            model=voice_agent.config.stt_model,
            language=voice_agent.config.language,
        ),
        llm=openai.LLM(  # Large Language Model
            model=voice_agent.config.llm_model,
        ),
        tts=cartesia.TTS(  # Text-to-Speech
            model_id=voice_agent.config.tts_model,
            voice={
                "id": voice_agent.config.tts_voice_id,
                "experimental_controls": {
                    "speed": "normal",
                    "emotion": [],
                },
            },
            language=voice_agent.config.language,
            output_format={
                "container": "raw",
                "encoding": "pcm_f32le",
                "sample_rate": 22050,
            },
        ),
    )
    
    # Start the session
    await session.start(agent=agent, room=ctx.room)
    
    # Generate initial greeting
    greeting = """Hello! I'm your AI assistant with knowledge about the articles 
    you've provided. Feel free to ask me questions about them or request specific 
    information. What would you like to know?"""
    
    await session.generate_reply(instructions=greeting)
    
    logger.info("Agent session started successfully")


def initialize_agent(
    article_urls: List[str],
    config: Optional[Config] = None
) -> WorkerOptions:
    """
    Initialize the voice agent with article URLs.
    
    This function prepares the agent with article knowledge
    and returns WorkerOptions for running the agent.
    
    Args:
        article_urls: List of article URLs to process
        config: Optional configuration (uses defaults if not provided)
        
    Returns:
        WorkerOptions configured for the agent
    """
    global voice_agent
    
    # Use provided config or create from environment
    if config is None:
        config = Config.from_env()
    
    # Create and prepare the voice agent
    voice_agent = VoiceAgent(config)
    voice_agent.add_article_urls(article_urls)
    voice_agent.prepare_knowledge_base()
    
    # Return worker options
    # Note: Updated to current LiveKit Agents API (v1.0+)
    return WorkerOptions(
        entrypoint_fnc=entrypoint
    )


def get_article_urls_from_env() -> List[str]:
    """
    Get article URLs from environment variables.
    
    This checks for ARTICLE_URLS environment variable and falls back to examples.
    
    Returns:
        List of article URLs to process
    """
    # Check environment variable first
    env_urls = os.getenv("ARTICLE_URLS", "")
    if env_urls:
        urls = [url.strip() for url in env_urls.split(",") if url.strip()]
        logger.info(f"Using {len(urls)} article URLs from ARTICLE_URLS environment variable")
        return urls
    
    # Fallback URLs - replace with your articles
    example_urls = [
        # Replace these with your actual article URLs:
        "https://github.blog/2019-03-29-leader-spotlight-erin-spiceland/",
        "https://docs.livekit.io/agents/",
        # Add your articles here:
        # "https://your-website.com/important-article",
        # "https://medium.com/@you/your-post",
        # "https://blog.yourcompany.com/product-update"
    ]
    logger.info(f"Using {len(example_urls)} example article URLs (set ARTICLE_URLS env var for custom URLs)")
    return example_urls


def create_worker_options(config: Optional[Config] = None) -> WorkerOptions:
    """
    Create WorkerOptions for the LiveKit CLI.
    
    This is the main function that sets up the agent for production deployment.
    
    Args:
        config: Optional configuration (uses defaults if not provided)
        
    Returns:
        WorkerOptions instance for the LiveKit CLI
    """
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Initializing voice agent for LiveKit CLI...")
    
    # Get article URLs from environment or fallback to examples
    article_urls = get_article_urls_from_env()
    
    # Initialize agent with articles
    worker_options = initialize_agent(article_urls, config)
    logger.info("Voice agent initialized and ready for LiveKit CLI")
    
    return worker_options


# Main entry point for LiveKit CLI
if __name__ == "__main__":
    # Load configuration from environment
    try:
        config = Config.from_env()
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.info("Please set the required environment variables (see .env.example)")
        exit(1)
    
    # Create worker options and run with LiveKit CLI
    # This supports all CLI commands: start, dev, console, etc.
    worker_options = create_worker_options(config)
    cli.run_app(worker_options)