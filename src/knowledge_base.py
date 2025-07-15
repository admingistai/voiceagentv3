"""
Knowledge Base Module

This module manages the agent's knowledge base by processing article text
with OpenAI's API. It creates a searchable knowledge store that the voice
agent can query during conversations.

Key Features:
- Process raw article text into structured knowledge
- Create embeddings for semantic search
- Store and retrieve relevant information
- Support multiple articles in the knowledge base
- Intelligent context generation for conversations
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import openai
from openai import OpenAI

# Configure logging for this module
logger = logging.getLogger(__name__)


class KnowledgeBase:
    """
    Manages article-based knowledge for the voice agent.
    
    This class processes article text using OpenAI's API to create
    a searchable knowledge base. It generates summaries, extracts
    key points, and provides context for agent conversations.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize the KnowledgeBase with OpenAI API.
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use for processing (default: gpt-4o-mini)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.knowledge_store: List[Dict[str, Any]] = []
        logger.info(f"KnowledgeBase initialized with model={model}")
    
    def process_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an article into structured knowledge.
        
        This method uses OpenAI to:
        1. Generate a concise summary
        2. Extract key points and facts
        3. Identify main topics
        4. Create conversational context
        
        Args:
            article: Article dictionary from ArticleExtractor
            
        Returns:
            Processed knowledge dictionary containing:
                - 'summary': Concise article summary
                - 'key_points': List of main points
                - 'topics': List of topics covered
                - 'context': Conversational context
                - 'metadata': Original article metadata
        """
        try:
            logger.info(f"Processing article: {article.get('title', 'Untitled')}")
            
            # Prepare the article text with metadata
            article_text = self._format_article_for_processing(article)
            
            # Generate comprehensive knowledge extraction
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a knowledge extraction expert. Process the given article and extract:
                        1. A concise summary (2-3 sentences)
                        2. Key points and important facts (5-10 bullet points)
                        3. Main topics covered (3-5 topics)
                        4. Conversational context (what someone should know to discuss this article)
                        
                        Return the result as a JSON object with keys: summary, key_points, topics, context"""
                    },
                    {
                        "role": "user",
                        "content": article_text
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent extraction
                response_format={ "type": "json_object" }  # Ensure JSON response
            )
            
            # Parse the response
            extracted = json.loads(response.choices[0].message.content)
            
            # Create the knowledge entry
            knowledge_entry = {
                'id': f"article_{datetime.now().timestamp()}",
                'processed_at': datetime.now().isoformat(),
                'summary': extracted.get('summary', ''),
                'key_points': extracted.get('key_points', []),
                'topics': extracted.get('topics', []),
                'context': extracted.get('context', ''),
                'metadata': {
                    'title': article.get('title'),
                    'author': article.get('author'),
                    'date': article.get('date'),
                    'url': article.get('url'),
                    'word_count': article.get('word_count')
                },
                'full_text': article['text']  # Keep full text for detailed queries
            }
            
            # Add to knowledge store
            self.knowledge_store.append(knowledge_entry)
            
            logger.info(f"Successfully processed article into knowledge base")
            return knowledge_entry
            
        except Exception as e:
            logger.error(f"Error processing article: {str(e)}")
            raise
    
    def add_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process and add multiple articles to the knowledge base.
        
        Args:
            articles: List of article dictionaries from ArticleExtractor
            
        Returns:
            List of processed knowledge entries
        """
        processed = []
        
        for article in articles:
            try:
                knowledge = self.process_article(article)
                processed.append(knowledge)
            except Exception as e:
                logger.error(f"Failed to process article {article.get('url')}: {str(e)}")
                continue
        
        logger.info(f"Added {len(processed)} articles to knowledge base")
        return processed
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search the knowledge base for relevant information.
        
        This method finds the most relevant knowledge entries
        for a given query using semantic similarity.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of relevant knowledge entries
        """
        if not self.knowledge_store:
            logger.warning("Knowledge base is empty")
            return []
        
        try:
            # For now, use a simple relevance scoring
            # In production, you might want to use embeddings for better search
            results = []
            
            for entry in self.knowledge_store:
                # Calculate relevance score based on query presence in key fields
                score = 0
                query_lower = query.lower()
                
                # Check summary
                if query_lower in entry['summary'].lower():
                    score += 3
                
                # Check key points
                for point in entry['key_points']:
                    if query_lower in point.lower():
                        score += 2
                
                # Check topics
                for topic in entry['topics']:
                    if query_lower in topic.lower():
                        score += 2
                
                # Check context
                if query_lower in entry['context'].lower():
                    score += 1
                
                if score > 0:
                    results.append((score, entry))
            
            # Sort by score and return top_k
            results.sort(key=lambda x: x[0], reverse=True)
            return [entry for score, entry in results[:top_k]]
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            return []
    
    def get_conversation_context(self, max_articles: int = 3) -> str:
        """
        Generate conversation context from the knowledge base.
        
        This method creates a context string that can be used to
        inform the voice agent about the available knowledge.
        
        Args:
            max_articles: Maximum number of articles to include in context
            
        Returns:
            Context string for the voice agent
        """
        if not self.knowledge_store:
            return "No articles have been loaded into the knowledge base yet."
        
        # Get the most recent articles
        recent_articles = self.knowledge_store[-max_articles:]
        
        context_parts = [
            "I have knowledge about the following articles:",
            ""
        ]
        
        for i, entry in enumerate(recent_articles, 1):
            title = entry['metadata'].get('title', 'Untitled Article')
            summary = entry['summary']
            topics = ", ".join(entry['topics'])
            
            context_parts.append(f"{i}. {title}")
            context_parts.append(f"   Summary: {summary}")
            context_parts.append(f"   Topics: {topics}")
            context_parts.append("")
        
        context_parts.append("I can discuss any of these topics in detail based on the articles I've processed.")
        
        return "\n".join(context_parts)
    
    def get_detailed_info(self, topic: str) -> Optional[str]:
        """
        Get detailed information about a specific topic.
        
        This method searches for the topic and returns detailed
        information from the most relevant article.
        
        Args:
            topic: Topic to get information about
            
        Returns:
            Detailed information string or None if not found
        """
        results = self.search(topic, top_k=1)
        
        if not results:
            return None
        
        entry = results[0]
        
        # Build detailed response
        details = []
        details.append(f"Based on '{entry['metadata'].get('title', 'the article')}', here's what I know about {topic}:")
        details.append("")
        details.append(entry['summary'])
        details.append("")
        details.append("Key points:")
        
        for point in entry['key_points']:
            details.append(f"• {point}")
        
        return "\n".join(details)
    
    def _format_article_for_processing(self, article: Dict[str, Any]) -> str:
        """
        Format article for OpenAI processing.
        
        Args:
            article: Article dictionary
            
        Returns:
            Formatted article text
        """
        parts = []
        
        # Add metadata if available
        if article.get('title'):
            parts.append(f"Title: {article['title']}")
        
        if article.get('author'):
            parts.append(f"Author: {article['author']}")
        
        if article.get('date'):
            parts.append(f"Date: {article['date']}")
        
        parts.append("")
        parts.append("Article Content:")
        parts.append(article['text'])
        
        return "\n".join(parts)
    
    def save_to_file(self, filepath: str):
        """
        Save the knowledge base to a JSON file.
        
        Args:
            filepath: Path to save the knowledge base
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_store, f, indent=2, ensure_ascii=False)
            logger.info(f"Knowledge base saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving knowledge base: {str(e)}")
            raise
    
    def load_from_file(self, filepath: str):
        """
        Load a knowledge base from a JSON file.
        
        Args:
            filepath: Path to load the knowledge base from
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.knowledge_store = json.load(f)
            logger.info(f"Knowledge base loaded from {filepath}")
        except Exception as e:
            logger.error(f"Error loading knowledge base: {str(e)}")
            raise


# Example usage and testing
if __name__ == "__main__":
    # Set up logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example article for testing
    test_article = {
        'text': "This is a test article about artificial intelligence...",
        'title': "The Future of AI",
        'author': "John Doe",
        'date': "2024-01-15",
        'url': "https://example.com/ai-article",
        'word_count': 500
    }
    
    # Create knowledge base (you would use a real API key)
    kb = KnowledgeBase(api_key="your-api-key-here")
    
    print("Knowledge base created successfully")