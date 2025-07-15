"""
Configuration Module

This module handles all configuration and environment variables for the voice agent.
It provides a centralized way to manage API keys, model selections, and other settings.

Key Features:
- Environment variable validation
- Default values for all settings
- Type-safe configuration access
- Support for different deployment environments
"""

import os
import logging
from typing import Optional
from dataclasses import dataclass

# Configure logging for this module
logger = logging.getLogger(__name__)


@dataclass
class Config:
    """
    Configuration class for the voice agent.
    
    This dataclass holds all configuration values needed by the agent,
    including API keys, model selections, and service settings.
    """
    
    # Required fields (no defaults) - must come first
    # LiveKit Configuration
    livekit_url: str
    livekit_api_key: str
    livekit_api_secret: str
    
    # OpenAI Configuration
    openai_api_key: str
    
    # Deepgram Configuration
    deepgram_api_key: str
    
    # Cartesia Configuration
    cartesia_api_key: str
    
    # Optional fields (with defaults) - must come after required fields
    # OpenAI Settings
    llm_model: str = "gpt-4o-mini"  # Default to cost-effective model
    
    # Deepgram Settings
    stt_model: str = "nova-3"  # Latest and most accurate model
    
    # Cartesia Settings
    tts_model: str = "sonic-2"  # High-quality voice model
    tts_voice_id: str = "a0e99841-438c-4a64-b679-ae501e7d6091"  # Default voice
    
    # General Settings
    language: str = "en"  # Language code
    log_level: str = "INFO"  # Logging level
    
    @classmethod
    def from_env(cls) -> "Config":
        """
        Create configuration from environment variables.
        
        This method reads all required environment variables and
        creates a Config instance. It validates that required
        variables are present and provides helpful error messages.
        
        Returns:
            Config instance with values from environment
            
        Raises:
            ValueError: If required environment variables are missing
        """
        # Check for required environment variables
        required_vars = [
            "LIVEKIT_URL",
            "LIVEKIT_API_KEY",
            "LIVEKIT_API_SECRET",
            "OPENAI_API_KEY",
            "DEEPGRAM_API_KEY",
            "CARTESIA_API_KEY",
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                "Please set these in your .env file or environment."
            )
        
        # Create config with environment values
        config = cls(
            # LiveKit
            livekit_url=os.getenv("LIVEKIT_URL", ""),
            livekit_api_key=os.getenv("LIVEKIT_API_KEY", ""),
            livekit_api_secret=os.getenv("LIVEKIT_API_SECRET", ""),
            
            # OpenAI
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            
            # Deepgram
            deepgram_api_key=os.getenv("DEEPGRAM_API_KEY", ""),
            stt_model=os.getenv("STT_MODEL", "nova-3"),
            
            # Cartesia
            cartesia_api_key=os.getenv("CARTESIA_API_KEY", ""),
            tts_model=os.getenv("TTS_MODEL", "sonic-2"),
            tts_voice_id=os.getenv("TTS_VOICE_ID", "a0e99841-438c-4a64-b679-ae501e7d6091"),
            
            # General
            language=os.getenv("LANGUAGE", "en"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
        
        logger.info("Configuration loaded from environment variables")
        return config
    
    def validate(self) -> bool:
        """
        Validate the configuration.
        
        This method checks that all required values are present
        and valid. It's useful for early error detection.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Check LiveKit configuration
        if not self.livekit_url:
            raise ValueError("LIVEKIT_URL is required")
        
        if not self.livekit_url.startswith(("ws://", "wss://")):
            raise ValueError("LIVEKIT_URL must start with ws:// or wss://")
        
        if not self.livekit_api_key or not self.livekit_api_secret:
            raise ValueError("LiveKit API credentials are required")
        
        # Check API keys
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        
        if not self.deepgram_api_key:
            raise ValueError("DEEPGRAM_API_KEY is required")
        
        if not self.cartesia_api_key:
            raise ValueError("CARTESIA_API_KEY is required")
        
        # Validate model selections
        valid_llm_models = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
        if self.llm_model not in valid_llm_models:
            logger.warning(f"Unusual LLM model: {self.llm_model}")
        
        valid_stt_models = ["nova-3", "nova-2", "enhanced", "base"]
        if self.stt_model not in valid_stt_models:
            logger.warning(f"Unusual STT model: {self.stt_model}")
        
        valid_tts_models = ["sonic-2", "sonic", "aura-2"]
        if self.tts_model not in valid_tts_models:
            logger.warning(f"Unusual TTS model: {self.tts_model}")
        
        # Validate language code
        if len(self.language) != 2:
            logger.warning(f"Language code should be 2 characters: {self.language}")
        
        logger.info("Configuration validated successfully")
        return True
    
    def mask_sensitive(self) -> dict:
        """
        Get configuration as dictionary with masked sensitive values.
        
        This is useful for logging configuration without exposing
        API keys and secrets.
        
        Returns:
            Dictionary with masked sensitive values
        """
        return {
            "livekit_url": self.livekit_url,
            "livekit_api_key": self._mask_value(self.livekit_api_key),
            "livekit_api_secret": self._mask_value(self.livekit_api_secret),
            "openai_api_key": self._mask_value(self.openai_api_key),
            "llm_model": self.llm_model,
            "deepgram_api_key": self._mask_value(self.deepgram_api_key),
            "stt_model": self.stt_model,
            "cartesia_api_key": self._mask_value(self.cartesia_api_key),
            "tts_model": self.tts_model,
            "tts_voice_id": self.tts_voice_id,
            "language": self.language,
            "log_level": self.log_level,
        }
    
    def _mask_value(self, value: str) -> str:
        """
        Mask sensitive value for logging.
        
        Args:
            value: Value to mask
            
        Returns:
            Masked value showing only first 4 and last 4 characters
        """
        if not value or len(value) < 12:
            return "***"
        
        return f"{value[:4]}...{value[-4:]}"
    
    def setup_logging(self):
        """
        Set up logging based on configuration.
        
        This method configures the logging system with the
        specified log level and format.
        """
        log_level = getattr(logging, self.log_level.upper(), logging.INFO)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        logger.info(f"Logging configured with level: {self.log_level}")
    
    @classmethod
    def from_file(cls, filepath: str) -> "Config":
        """
        Load configuration from a .env file.
        
        This method is useful for local development where you
        want to load configuration from a file.
        
        Args:
            filepath: Path to .env file
            
        Returns:
            Config instance
        """
        # Simple .env file parser
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            
            logger.info(f"Loaded environment from {filepath}")
        else:
            logger.warning(f"Configuration file not found: {filepath}")
        
        return cls.from_env()


# Example usage and testing
if __name__ == "__main__":
    # Set up basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test configuration loading
    try:
        # Try to load from environment
        config = Config.from_env()
        config.validate()
        
        print("Configuration loaded successfully!")
        print("Masked configuration:")
        for key, value in config.mask_sensitive().items():
            print(f"  {key}: {value}")
            
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("\nExample .env file:")
        print("""
# LiveKit Configuration
LIVEKIT_URL=wss://your-livekit-instance.livekit.cloud
LIVEKIT_API_KEY=your-livekit-api-key
LIVEKIT_API_SECRET=your-livekit-api-secret

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
LLM_MODEL=gpt-4o-mini

# Deepgram Configuration
DEEPGRAM_API_KEY=your-deepgram-api-key
STT_MODEL=nova-3

# Cartesia Configuration
CARTESIA_API_KEY=your-cartesia-api-key
TTS_MODEL=sonic-2
TTS_VOICE_ID=a0e99841-438c-4a64-b679-ae501e7d6091

# General Settings
LANGUAGE=en
LOG_LEVEL=INFO
""")