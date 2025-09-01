"""
Utility functions for AI Search API CrewAI integration (new tools API)

- Compatible with CrewAI >= 0.175.0
- Returns crewai.tools.BaseTool instances
"""

from __future__ import annotations

from typing import List, Optional
from crewai.tools import BaseTool

from .tool import AISearchTool, AISearchToolConfig


def create_research_tools(
    api_key: str,
    specialized_domains: Optional[List[str]] = None
) -> List[BaseTool]:
    """
    Create research tools (general + optional domain-focused).

    Args:
        api_key: AI Search API key.
        specialized_domains: List of domain names (strings). If given,
                             creates extra tools named "<Domain>_Search".

    Returns:
        List[BaseTool]: Tool instances ready to pass to Agent(tools=[...]).
    """
    tools: List[BaseTool] = []

    # General purpose search tool
    general_search = AISearchTool(
        api_key=api_key,
        config=AISearchToolConfig(
            default_response_type="markdown",
            include_sources=True,
            verbose=False,
        ),
    )
    # You can customize the instance name/description
    general_search.name = "General_Search"
    general_search.description = "General purpose intelligent web search for any topic."
    tools.append(general_search)

    # Domain-focused tools (names/descriptions guide the LLM to pick them)
    if specialized_domains:
        for domain in specialized_domains:
            spec_tool = AISearchTool(
                api_key=api_key,
                config=AISearchToolConfig(
                    default_response_type="markdown",
                    include_sources=True,
                    verbose=False,
                ),
            )
            safe_domain = domain.replace(" ", "_")
            spec_tool.name = f"{safe_domain}_Search"
            spec_tool.description = (
                f"Specialized web search for {domain} related topics."
            )
            tools.append(spec_tool)

    return tools


def create_fact_checker_tool(api_key: str) -> BaseTool:
    """
    Create a fact-checking tool instance.

    Args:
        api_key: AI Search API key.

    Returns:
        BaseTool: Configured fact-checking tool.
    """
    fact_checker = AISearchTool(
        api_key=api_key,
        config=AISearchToolConfig(
            default_response_type="markdown",
            include_sources=True,
            verbose=True,  # verbose helps when fact-checking
        ),
    )
    fact_checker.name = "Fact_Checker"
    fact_checker.description = (
        "Verify facts and claims with source citations. "
        "Use this to fact-check statements and find authoritative sources."
    )
    return fact_checker
