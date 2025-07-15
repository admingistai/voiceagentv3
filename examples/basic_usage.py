"""
Basic Usage Example

This script demonstrates how to use the Voice Agent Module to:
1. Extract content from article URLs
2. Build a knowledge base
3. Start a voice conversation

Requirements:
- Set up your .env file with all required API keys
- Have article URLs ready to process
"""

import os
import sys
import logging

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.agent import run_agent, VoiceAgent
from src.article_extractor import ArticleExtractor
from src.knowledge_base import KnowledgeBase


def example_basic_usage():
    """
    Basic example: Run the agent with a few article URLs.
    
    This is the simplest way to get started - just provide
    URLs and let the agent handle everything.
    """
    print("=== Basic Usage Example ===\n")
    
    # Example article URLs - replace with real articles
    article_urls = [
        "https://www.nature.com/articles/s41586-023-06221-2",  # Example: AI research
        "https://openai.com/blog/gpt-4",                       # Example: GPT-4 announcement
        "https://www.anthropic.com/index/claude-2",            # Example: Claude 2
    ]
    
    print(f"Processing {len(article_urls)} articles...")
    print("Articles:")
    for i, url in enumerate(article_urls, 1):
        print(f"  {i}. {url}")
    print()
    
    # Run the agent with these articles
    # This will:
    # 1. Extract text from each URL
    # 2. Process into knowledge base
    # 3. Start voice conversation
    run_agent(article_urls)


def example_step_by_step():
    """
    Step-by-step example showing each component.
    
    This example demonstrates how to use each component
    individually for more control over the process.
    """
    print("=== Step-by-Step Example ===\n")
    
    # Step 1: Load configuration
    print("Step 1: Loading configuration...")
    try:
        config = Config.from_env()
        config.validate()
        print("✓ Configuration loaded and validated")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        return
    
    # Step 2: Extract articles
    print("\nStep 2: Extracting articles...")
    extractor = ArticleExtractor(timeout=30)
    
    test_urls = [
        "https://example.com/article1",
        "https://example.com/article2",
    ]
    
    articles = []
    for url in test_urls:
        print(f"  Extracting: {url}")
        article = extractor.extract_from_url(url)
        if article:
            print(f"    ✓ Extracted {article['word_count']} words")
            articles.append(article)
        else:
            print(f"    ✗ Failed to extract")
    
    # Step 3: Build knowledge base
    print(f"\nStep 3: Building knowledge base from {len(articles)} articles...")
    kb = KnowledgeBase(api_key=config.openai_api_key)
    
    for article in articles:
        try:
            knowledge = kb.process_article(article)
            print(f"  ✓ Processed: {article.get('title', 'Untitled')}")
            print(f"    - Summary: {knowledge['summary'][:100]}...")
            print(f"    - Topics: {', '.join(knowledge['topics'][:3])}")
        except Exception as e:
            print(f"  ✗ Failed to process: {e}")
    
    # Step 4: Test knowledge base search
    print("\nStep 4: Testing knowledge base search...")
    test_query = "artificial intelligence"
    results = kb.search(test_query, top_k=2)
    print(f"  Search for '{test_query}' returned {len(results)} results")
    
    # Step 5: Start voice agent
    print("\nStep 5: Starting voice agent...")
    print("  The agent is now ready for voice conversations!")
    print("  You can ask about the articles you've processed.")
    
    # Create and run agent
    agent = VoiceAgent(config)
    agent.knowledge_base = kb  # Use our prepared knowledge base
    
    # Note: In production, you would use run_agent()
    # This is just to show the components


def example_custom_configuration():
    """
    Example with custom configuration.
    
    This shows how to override default settings for
    different models, voices, and languages.
    """
    print("=== Custom Configuration Example ===\n")
    
    # Create custom configuration
    config = Config.from_env()
    
    # Override defaults
    config.llm_model = "gpt-4o"  # Use more powerful model
    config.stt_model = "nova-2"  # Use different STT model
    config.tts_voice_id = "custom-voice-id"  # Use custom voice
    config.language = "es"  # Spanish language
    
    print("Custom configuration:")
    print(f"  LLM Model: {config.llm_model}")
    print(f"  STT Model: {config.stt_model}")
    print(f"  TTS Voice: {config.tts_voice_id}")
    print(f"  Language: {config.language}")
    
    # Run with custom config
    article_urls = ["https://example.com/spanish-article"]
    run_agent(article_urls, config=config)


def example_knowledge_base_operations():
    """
    Example showing knowledge base operations.
    
    This demonstrates how to work with the knowledge base
    directly for custom applications.
    """
    print("=== Knowledge Base Operations Example ===\n")
    
    # Load configuration
    config = Config.from_env()
    
    # Create knowledge base
    kb = KnowledgeBase(api_key=config.openai_api_key)
    
    # Example article data (normally from extractor)
    article = {
        'text': """
        Artificial Intelligence has made remarkable progress in recent years.
        Large language models like GPT-4 and Claude can understand and generate
        human-like text. Computer vision systems can identify objects with
        superhuman accuracy. These advances are transforming industries from
        healthcare to finance.
        """,
        'title': "AI Progress in 2024",
        'author': "Dr. Jane Smith",
        'url': "https://example.com/ai-2024",
        'word_count': 50
    }
    
    # Process the article
    print("Processing article...")
    knowledge = kb.process_article(article)
    
    print(f"\nProcessed knowledge:")
    print(f"  Summary: {knowledge['summary']}")
    print(f"  Key Points: {len(knowledge['key_points'])} points")
    print(f"  Topics: {', '.join(knowledge['topics'])}")
    
    # Search operations
    print("\nSearch examples:")
    queries = ["GPT-4", "healthcare", "computer vision"]
    
    for query in queries:
        results = kb.search(query, top_k=1)
        print(f"  '{query}': {len(results)} results found")
    
    # Get conversation context
    context = kb.get_conversation_context()
    print(f"\nConversation context:\n{context}")
    
    # Save and load knowledge base
    print("\nSaving knowledge base...")
    kb.save_to_file("knowledge_backup.json")
    print("✓ Saved to knowledge_backup.json")


def example_error_handling():
    """
    Example showing proper error handling.
    
    This demonstrates how to handle common errors
    gracefully in production environments.
    """
    print("=== Error Handling Example ===\n")
    
    # Handle missing configuration
    try:
        config = Config.from_env()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("\nTo fix this:")
        print("1. Copy .env.example to .env")
        print("2. Add your API keys")
        print("3. Try again")
        return
    
    # Handle extraction errors
    extractor = ArticleExtractor()
    problematic_urls = [
        "not-a-valid-url",
        "https://blocked-site.com/article",
        "https://example.com/404",
    ]
    
    print("Testing error handling for problematic URLs:")
    for url in problematic_urls:
        article = extractor.extract_from_url(url)
        if article:
            print(f"  ✓ {url}: Success")
        else:
            print(f"  ✗ {url}: Failed (handled gracefully)")
    
    # Handle API errors
    print("\nTesting API error handling:")
    kb = KnowledgeBase(api_key="invalid-key")
    
    try:
        kb.process_article({
            'text': "Test article",
            'url': "https://example.com"
        })
    except Exception as e:
        print(f"  API error caught: {type(e).__name__}")
        print("  This is expected with an invalid API key")


def main():
    """
    Main function to run examples.
    
    Uncomment the example you want to run.
    """
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Choose which example to run
    # Uncomment the one you want:
    
    example_basic_usage()
    # example_step_by_step()
    # example_custom_configuration()
    # example_knowledge_base_operations()
    # example_error_handling()


if __name__ == "__main__":
    print("Voice Agent Module - Examples\n")
    print("Make sure you have:")
    print("1. Set up your .env file with all API keys")
    print("2. Installed all requirements")
    print("3. Have a LiveKit instance running")
    print("\n" + "="*50 + "\n")
    
    main()