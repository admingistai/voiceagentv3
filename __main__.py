"""
Main entry point for the Voice Agent Module.

This allows running the module directly with:
    python -m voice-agent-module

Or from the project directory:
    python .
"""

import os
import sys
import argparse
import logging
from typing import List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import Config
from src.agent import run_agent


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Voice Agent Module - Process articles and start voice conversations"
    )
    
    parser.add_argument(
        "--urls",
        type=str,
        help="Comma-separated list of article URLs to process",
        default=os.getenv("ARTICLE_URLS", "")
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Path to .env configuration file",
        default=".env"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=os.getenv("LOG_LEVEL", "INFO"),
        help="Logging level"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run in test mode (validate configuration only)"
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    print("""
    ╔══════════════════════════════════════════╗
    ║       Voice Agent Module v1.0.0          ║
    ║                                          ║
    ║  🎙️  Real-time voice conversations       ║
    ║  📰 Article knowledge extraction         ║
    ║  🚀 Railway-ready deployment             ║
    ╚══════════════════════════════════════════╝
    """)
    
    try:
        # Load configuration
        if args.config and os.path.exists(args.config):
            logger.info(f"Loading configuration from {args.config}")
            config = Config.from_file(args.config)
        else:
            logger.info("Loading configuration from environment")
            config = Config.from_env()
        
        # Validate configuration
        config.validate()
        logger.info("Configuration validated successfully")
        
        # Test mode - just validate and exit
        if args.test:
            print("\n✓ Configuration test passed!")
            print("\nConfiguration summary:")
            for key, value in config.mask_sensitive().items():
                print(f"  {key}: {value}")
            return 0
        
        # Parse article URLs
        article_urls: List[str] = []
        
        if args.urls:
            article_urls = [url.strip() for url in args.urls.split(",") if url.strip()]
        
        if not article_urls:
            print("\n⚠️  No article URLs provided!")
            print("\nYou can provide URLs in two ways:")
            print("1. Command line: python -m voice-agent-module --urls 'url1,url2'")
            print("2. Environment variable: ARTICLE_URLS='url1,url2'")
            print("\nStarting agent without articles - you can still have conversations.")
            response = input("\nContinue anyway? (y/n): ")
            if response.lower() != 'y':
                return 0
        else:
            print(f"\n📰 Processing {len(article_urls)} articles:")
            for i, url in enumerate(article_urls, 1):
                print(f"   {i}. {url}")
        
        print("\n🚀 Starting voice agent...")
        print("   This may take a moment to initialize all services.")
        print("\n   Once started, you can speak to the agent about the articles!")
        print("   Press Ctrl+C to stop.\n")
        
        # Run the agent
        run_agent(article_urls, config)
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
        return 0
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print("\n❌ Configuration Error:")
        print(f"   {e}")
        print("\n💡 Tip: Copy .env.example to .env and add your API keys")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())