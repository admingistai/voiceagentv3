"""
Article Extractor Module

This module handles extracting text content from article URLs using trafilatura.
It provides robust web scraping with fallback options and proper error handling.

Key Features:
- Automatic article text extraction
- Metadata extraction (title, author, date)
- Content cleaning and formatting
- Error handling for failed extractions
- Support for various article formats and websites
"""

import logging
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import trafilatura
from trafilatura.settings import use_config

# Configure logging for this module
logger = logging.getLogger(__name__)

# Configure trafilatura for better extraction
# This config improves extraction quality and handles edge cases
TRAFILATURA_CONFIG = use_config()
TRAFILATURA_CONFIG.set("DEFAULT", "EXTRACTION_TIMEOUT", "30")  # 30 second timeout
TRAFILATURA_CONFIG.set("DEFAULT", "EXTENSIVE_EXTRACTION", "true")  # More thorough extraction


class ArticleExtractor:
    """
    Extracts and processes text content from article URLs.
    
    This class provides methods to:
    - Download article content from URLs
    - Extract main text and metadata
    - Clean and format the extracted content
    - Handle extraction errors gracefully
    """
    
    def __init__(self, timeout: int = 30):
        """
        Initialize the ArticleExtractor.
        
        Args:
            timeout: Maximum time to wait for article download (seconds)
        """
        self.timeout = timeout
        logger.info(f"ArticleExtractor initialized with timeout={timeout}s")
    
    def extract_from_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract article content and metadata from a URL.
        
        This method attempts to download and extract the main content from
        an article URL. It uses trafilatura's advanced extraction features
        to get clean text and metadata.
        
        Args:
            url: The URL of the article to extract
            
        Returns:
            Dictionary containing:
                - 'text': The main article text
                - 'title': Article title (if available)
                - 'author': Article author (if available)
                - 'date': Publication date (if available)
                - 'url': The original URL
                - 'domain': The domain of the article
            Returns None if extraction fails
        """
        try:
            # Validate URL format
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                logger.error(f"Invalid URL format: {url}")
                return None
            
            logger.info(f"Extracting article from: {url}")
            
            # Download the article content
            # include_comments=False to avoid extracting comment sections
            # include_tables=False to focus on main text content
            # Note: trafilatura.fetch_url() doesn't accept timeout parameter
            downloaded = trafilatura.fetch_url(url)
            
            if not downloaded:
                logger.error(f"Failed to download content from: {url}")
                return None
            
            # Extract the main content
            # output_format='txt' for plain text (easier for LLM processing)
            # include_links=False to avoid URL clutter in text
            text = trafilatura.extract(
                downloaded,
                output_format='txt',
                include_comments=False,
                include_tables=False,
                include_links=False,
                deduplicate=True,  # Remove duplicate content
                config=TRAFILATURA_CONFIG
            )
            
            if not text:
                logger.error(f"Failed to extract text from: {url}")
                return None
            
            # Extract metadata
            # This includes title, author, date, and other useful information
            metadata = trafilatura.extract_metadata(downloaded)
            
            # Build the result dictionary
            result = {
                'text': text,
                'url': url,
                'domain': parsed_url.netloc,
                'title': metadata.title if metadata else None,
                'author': metadata.author if metadata else None,
                'date': metadata.date if metadata else None,
                'word_count': len(text.split())  # Approximate word count
            }
            
            logger.info(f"Successfully extracted {result['word_count']} words from: {url}")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting article from {url}: {str(e)}")
            return None
    
    def extract_multiple(self, urls: list[str]) -> list[Dict[str, Any]]:
        """
        Extract content from multiple URLs.
        
        This method processes multiple URLs and returns successfully
        extracted articles. Failed extractions are logged but don't
        stop the process.
        
        Args:
            urls: List of article URLs to extract
            
        Returns:
            List of successfully extracted articles
        """
        results = []
        
        for url in urls:
            # Extract each article
            article = self.extract_from_url(url)
            
            if article:
                results.append(article)
            else:
                logger.warning(f"Skipping failed extraction: {url}")
        
        logger.info(f"Extracted {len(results)} out of {len(urls)} articles")
        return results
    
    def format_for_knowledge_base(self, article: Dict[str, Any]) -> str:
        """
        Format extracted article for knowledge base ingestion.
        
        This method creates a formatted string that includes metadata
        and content, making it easier for the LLM to understand context.
        
        Args:
            article: Extracted article dictionary
            
        Returns:
            Formatted string ready for knowledge base processing
        """
        # Build formatted output with metadata
        formatted = []
        
        # Add metadata if available
        if article.get('title'):
            formatted.append(f"Title: {article['title']}")
        
        if article.get('author'):
            formatted.append(f"Author: {article['author']}")
        
        if article.get('date'):
            formatted.append(f"Date: {article['date']}")
        
        formatted.append(f"Source: {article['url']}")
        formatted.append("")  # Empty line separator
        
        # Add the main content
        formatted.append("Content:")
        formatted.append(article['text'])
        
        return "\n".join(formatted)


# Example usage and testing
if __name__ == "__main__":
    # Set up logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create an extractor instance
    extractor = ArticleExtractor()
    
    # Test with a sample URL
    test_url = "https://example.com/article"
    print(f"Testing extraction from: {test_url}")
    
    result = extractor.extract_from_url(test_url)
    if result:
        print(f"Extracted {result['word_count']} words")
        print(f"Title: {result.get('title', 'N/A')}")
        print(f"Formatted content preview:")
        formatted = extractor.format_for_knowledge_base(result)
        print(formatted[:500] + "..." if len(formatted) > 500 else formatted)
    else:
        print("Extraction failed")