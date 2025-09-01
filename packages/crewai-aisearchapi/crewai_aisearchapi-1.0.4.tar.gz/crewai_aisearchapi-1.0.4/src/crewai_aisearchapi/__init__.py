"""
CrewAI AI Search API Integration

Provides tools for integrating AI Search API with CrewAI agents.
"""

from .tool import AISearchTool, AISearchToolConfig, aisearch_tool
from .utils import create_research_tools, create_fact_checker_tool

__version__ = "1.0.4"
__all__ = [
    "AISearchTool",
    "AISearchToolConfig",
    "aisearch_tool",
    "create_research_tools",
    "create_fact_checker_tool",
]