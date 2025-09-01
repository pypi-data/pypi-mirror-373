"""
Utility functions for AI Search API CrewAI integration
"""

from typing import List, Dict, Any, Optional
from crewai import Tool
from .tool import AISearchTool, AISearchToolConfig, aisearch_tool


def create_research_tools(
    api_key: str,
    specialized_domains: Optional[List[str]] = None
) -> List[Tool]:
    """
    Create specialized research tools for different domains
    
    Args:
        api_key: AI Search API key
        specialized_domains: List of domains to create specialized tools for
        
    Returns:
        List of configured CrewAI Tools
    """
    tools = []
    
    # Create general purpose tool
    general_search = AISearchTool(
        api_key=api_key,
        config=AISearchToolConfig(
            default_response_type="markdown",
            include_sources=True,
            verbose=False
        )
    )
    general_tool = general_search.as_tool()
    general_tool.name = "General_Search"
    general_tool.description = "General purpose intelligent web search for any topic"
    tools.append(general_tool)
    
    # Create specialized tools if domains specified
    if specialized_domains:
        for domain in specialized_domains:
            specialized_search = AISearchTool(
                api_key=api_key,
                config=AISearchToolConfig(
                    default_response_type="markdown",
                    include_sources=True,
                    verbose=False
                )
            )
            specialized_tool = specialized_search.as_tool()
            specialized_tool.name = f"{domain.replace(' ', '_')}_Search"
            specialized_tool.description = f"Specialized web search for {domain} related topics"
            tools.append(specialized_tool)
    
    return tools


def create_fact_checker_tool(api_key: str) -> Tool:
    """
    Create a fact-checking specialized tool
    
    Args:
        api_key: AI Search API key
        
    Returns:
        Configured fact-checking Tool
    """
    fact_checker = AISearchTool(
        api_key=api_key,
        config=AISearchToolConfig(
            default_response_type="markdown",
            include_sources=True,
            verbose=True
        )
    )
    tool = fact_checker.as_tool()
    tool.name = "Fact_Checker"
    tool.description = (
        "Verify facts and claims with source citations. "
        "Use this to fact-check statements and find authoritative sources."
    )
    return tool
