"""
Utility functions for AI Search API CrewAI integration
"""

from typing import List, Dict, Any, Optional
from .tool import AISearchTool, AISearchToolConfig


def create_research_tools(
    api_key: str,
    specialized_domains: Optional[List[str]] = None
) -> List[AISearchTool]:
    """
    Create specialized research tools for different domains
    
    Args:
        api_key: AI Search API key
        specialized_domains: List of domains to create specialized tools for
        
    Returns:
        List of configured AI Search tools
    """
    tools = []
    
    # Create general purpose tool
    general_tool = AISearchTool(
        api_key=api_key,
        config=AISearchToolConfig(
            default_response_type="markdown",
            include_sources=True,
            verbose=False
        )
    )
    general_tool.name = "General Search"
    general_tool.description = "General purpose intelligent search for any topic"
    tools.append(general_tool)
    
    # Create specialized tools if domains specified
    if specialized_domains:
        for domain in specialized_domains:
            specialized_tool = AISearchTool(
                api_key=api_key,
                config=AISearchToolConfig(
                    default_response_type="markdown",
                    include_sources=True,
                    verbose=False
                )
            )
            specialized_tool.name = f"{domain} Search"
            specialized_tool.description = f"Specialized search for {domain} related topics"
            tools.append(specialized_tool)
    
    return tools


def create_fact_checker_tool(api_key: str) -> AISearchTool:
    """
    Create a fact-checking specialized tool
    
    Args:
        api_key: AI Search API key
        
    Returns:
        Configured fact-checking tool
    """
    tool = AISearchTool(
        api_key=api_key,
        config=AISearchToolConfig(
            default_response_type="markdown",
            include_sources=True,
            verbose=True
        )
    )
    tool.name = "Fact Checker"
    tool.description = (
        "Verify facts and claims with source citations. "
        "Use this to fact-check statements and find authoritative sources."
    )
    return tool