"""
CrewAI AI Search API Integration

Provides tools for integrating AI Search API with CrewAI agents.
"""

from .tool import AISearchTool, AISearchToolConfig, aisearch_tool

__version__ = "1.0.2"
__all__ = ["AISearchTool", "AISearchToolConfig", "aisearch_tool"]
