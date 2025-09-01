"""
AI Search API Tool for CrewAI

This module provides a CrewAI-compatible tool for performing intelligent searches
using the AI Search API.
"""

import os
import json
from typing import Optional, List, Dict, Any, Type, Callable
from dataclasses import dataclass, field

# Import from crewai directly - no crewai-tools dependency needed
from crewai import Tool
from pydantic import BaseModel, Field as PydanticField

# Import your client
from aisearchapi_client import AISearchAPIClient, ChatMessage, AISearchAPIError


@dataclass
class AISearchToolConfig:
    """Configuration for AI Search Tool"""
    api_key: Optional[str] = None
    base_url: str = "https://api.aisearchapi.io"
    timeout: int = 30
    default_response_type: str = "markdown"
    max_context_messages: int = 10
    include_sources: bool = True
    verbose: bool = False


class AISearchTool:
    """
    AI Search API Tool for CrewAI
    
    This tool enables CrewAI agents to perform intelligent searches with
    context awareness and semantic understanding using AI Search API.
    
    Example:
        ```python
        from crewai import Agent, Task, Crew
        from crewai_aisearchapi import AISearchTool
        
        # Initialize the tool
        search_tool = AISearchTool(api_key='your-api-key')
        
        # Create an agent with the tool
        researcher = Agent(
            role='Research Analyst',
            goal='Find accurate information',
            tools=[search_tool.as_tool()],
            verbose=True
        )
        
        # Use in a crew
        crew = Crew(
            agents=[researcher],
            tasks=[...],
            verbose=True
        )
        ```
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[AISearchToolConfig] = None
    ):
        """
        Initialize the AI Search Tool
        
        Args:
            api_key: API key for AI Search API (can also use AISEARCHAPI_API_KEY env var)
            config: Optional configuration object
        """
        # Setup configuration
        self.config = config or AISearchToolConfig()
        
        # Get API key from parameter, config, or environment
        self.api_key = (
            api_key or 
            self.config.api_key or 
            os.getenv('AISEARCHAPI_API_KEY')
        )
        
        if not self.api_key:
            raise ValueError(
                "API key is required. Provide it via parameter, "
                "config, or AISEARCHAPI_API_KEY environment variable"
            )
        
        # Initialize the client
        self.client = AISearchAPIClient(
            api_key=self.api_key,
            base_url=self.config.base_url,
            timeout=self.config.timeout
        )
        
        # Store conversation context
        self.context_history: List[ChatMessage] = []
    
    def search(
        self,
        query: str,
        context: Optional[str] = None,
        response_type: Optional[str] = None
    ) -> str:
        """
        Execute a search query
        
        Args:
            query: The search query
            context: Optional context string
            response_type: Response format ('text' or 'markdown')
            
        Returns:
            Formatted search results with sources
        """
        try:
            # Build context messages
            context_messages = []
            
            # Add provided context
            if context:
                context_messages.append(
                    ChatMessage(role='user', content=context)
                )
            
            # Add recent history if available
            if self.context_history:
                # Limit context to recent messages
                recent_context = self.context_history[-self.config.max_context_messages:]
                context_messages.extend(recent_context)
            
            # Use default response type if not specified
            if not response_type:
                response_type = self.config.default_response_type
            
            # Log if verbose
            if self.config.verbose:
                print(f"[AI Search] Query: {query}")
                if context:
                    print(f"[AI Search] Context: {context}")
            
            # Perform the search
            result = self.client.search(
                prompt=query,
                context=context_messages if context_messages else None,
                response_type=response_type
            )
            
            # Format the response
            formatted_response = self._format_response(result, query)
            
            # Update context history
            self._update_context(query, result.answer)
            
            return formatted_response
            
        except AISearchAPIError as e:
            error_msg = f"AI Search API Error: {e.description}"
            if e.status_code == 433:
                error_msg += "\n⚠️ Account quota exceeded. Please check your balance."
            elif e.status_code == 401:
                error_msg += "\n⚠️ Invalid API key. Please check your credentials."
            
            if self.config.verbose:
                print(f"[AI Search] Error: {error_msg}")
            
            return f"Search failed: {error_msg}"
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            if self.config.verbose:
                print(f"[AI Search] Error: {error_msg}")
            return f"Search failed: {error_msg}"
    
    def _format_response(self, result, query: str) -> str:
        """Format the search response"""
        parts = []
        
        # Add the main answer
        parts.append(result.answer)
        
        # Add sources if configured
        if self.config.include_sources and result.sources:
            parts.append("\n\n**Sources:**")
            for i, source in enumerate(result.sources, 1):
                parts.append(f"- [{i}] {source}")
        
        # Add metadata if verbose
        if self.config.verbose:
            parts.append(f"\n\n*Response time: {result.total_time}ms*")
        
        return "\n".join(parts)
    
    def _update_context(self, query: str, answer: str):
        """Update conversation context history"""
        # Store query as context for future searches
        self.context_history.append(
            ChatMessage(role='user', content=f"Previous query: {query[:200]}")
        )
        
        # Limit history size
        if len(self.context_history) > self.config.max_context_messages * 2:
            self.context_history = self.context_history[-self.config.max_context_messages:]
    
    def check_balance(self) -> Dict[str, Any]:
        """
        Check API credit balance
        
        Returns:
            Dictionary with balance information
        """
        try:
            balance = self.client.balance()
            return {
                "available_credits": balance.available_credits,
                "status": "active" if balance.available_credits > 0 else "depleted"
            }
        except AISearchAPIError as e:
            return {
                "error": e.description,
                "status": "error"
            }
    
    def clear_context(self):
        """Clear conversation context history"""
        self.context_history = []
        if self.config.verbose:
            print("[AI Search] Context history cleared")
    
    def as_tool(self) -> Tool:
        """
        Convert to CrewAI Tool object
        
        Returns:
            CrewAI Tool instance
        """
        return Tool(
            name="AI_Search",
            description=(
                "Perform intelligent web searches with context awareness. "
                "Input should be a search query string. "
                "Returns well-structured answers with source citations."
            ),
            func=self.search
        )


def aisearch_tool(
    api_key: Optional[str] = None,
    config: Optional[AISearchToolConfig] = None
) -> Tool:
    """
    Create a CrewAI Tool for AI Search API
    
    This is a convenience function that creates a ready-to-use Tool object.
    
    Args:
        api_key: API key for AI Search API
        config: Optional configuration
        
    Returns:
        CrewAI Tool instance
        
    Example:
        ```python
        from crewai import Agent
        from crewai_aisearchapi import aisearch_tool
        
        agent = Agent(
            role='Researcher',
            tools=[aisearch_tool(api_key='your-key')]
        )
        ```
    """
    search = AISearchTool(api_key=api_key, config=config)
    return search.as_tool()
