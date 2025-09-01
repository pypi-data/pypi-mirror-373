"""
AI Search API Tool for CrewAI (new tools API)

- Compatible with CrewAI >= 0.175.0
- Uses crewai.tools.BaseTool and args_schema
- Keeps config, context, and balance helpers
"""

from __future__ import annotations

import os
from typing import Optional, List, Dict, Any, Type

from dataclasses import dataclass
from pydantic import BaseModel, Field

from crewai.tools import BaseTool

# Your client SDK
from aisearchapi_client import AISearchAPIClient, ChatMessage, AISearchAPIError


# -----------------------------
# Config
# -----------------------------
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


# -----------------------------
# Input schema for the tool
# -----------------------------
class AISearchInput(BaseModel):
    query: str = Field(..., description="Search query text.")
    context: Optional[str] = Field(
        default=None,
        description="Optional extra context for the search."
    )
    response_type: Optional[str] = Field(
        default=None,
        description="Response format: 'text' or 'markdown'."
    )


# -----------------------------
# Tool implementation
# -----------------------------
class AISearchTool(BaseTool):
    """
    AI Search API Tool for CrewAI (BaseTool)

    Usage (CrewAI 0.175+):
        from crewai import Agent, Task, Crew
        from crewai_aisearchapi import AISearchTool

        search_tool = AISearchTool(api_key="your-key")

        agent = Agent(
            name="Research Analyst",
            role="Find accurate information",
            goal="Deliver clear answers with sources",
            tools=[search_tool],
            verbose=True
        )

        task = Task(description="Find info about Hyper-V benefits", agent=agent)
        crew = Crew(agents=[agent], tasks=[task], verbose=True)
        print(crew.kickoff())
    """

    # BaseTool attributes
    name: str = "AI_Search"
    description: str = (
        "Perform intelligent web searches with context awareness. "
        "Input should include a 'query' string. Optionally provide 'context' "
        "and 'response_type' ('text' or 'markdown'). Returns a structured answer "
        "and (optionally) source links."
    )
    args_schema: Type[BaseModel] = AISearchInput

    # Custom init (BaseTool allows __init__)
    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[AISearchToolConfig] = None
    ):
        super().__init__()
        self.config = config or AISearchToolConfig()

        # Resolve API key: param > config > env
        self.api_key = api_key or self.config.api_key or os.getenv("AISEARCHAPI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key is required. Pass api_key=..., set in config, "
                "or set AISEARCHAPI_API_KEY env var."
            )

        # Init client
        self.client = AISearchAPIClient(
            api_key=self.api_key,
            base_url=self.config.base_url,
            timeout=self.config.timeout,
        )

        # Keep short conversation context
        self.context_history: List[ChatMessage] = []

    # Main run method called by CrewAI
    def _run(
        self,
        query: str,
        context: Optional[str] = None,
        response_type: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        try:
            # Build context messages (optional)
            context_messages: List[ChatMessage] = []

            if context:
                context_messages.append(ChatMessage(role="user", content=context))

            if self.context_history:
                # limit to recent messages
                recent = self.context_history[-self.config.max_context_messages :]
                context_messages.extend(recent)

            # Default response type if missing
            if not response_type:
                response_type = self.config.default_response_type

            if self.config.verbose:
                print(f"[AI Search] Query: {query}")
                if context:
                    print(f"[AI Search] Extra context: {context}")

            # Call API
            result = self.client.search(
                prompt=query,
                context=context_messages if context_messages else None,
                response_type=response_type,
            )

            # Format
            formatted = self._format_response(result)
            # Update short history
            self._update_context(query, result.answer)
            return formatted

        except AISearchAPIError as e:
            msg = f"AI Search API Error: {e.description}"
            if e.status_code == 433:
                msg += "\n⚠️ Account quota exceeded. Please check your balance."
            elif e.status_code == 401:
                msg += "\n⚠️ Invalid API key. Please check your credentials."
            if self.config.verbose:
                print(f"[AI Search] Error: {msg}")
            return f"Search failed: {msg}"

        except Exception as e:
            msg = f"Unexpected error: {str(e)}"
            if self.config.verbose:
                print(f"[AI Search] Error: {msg}")
            return f"Search failed: {msg}"

    # Helpers
    def _format_response(self, result) -> str:
        parts: List[str] = [result.answer]

        if self.config.include_sources and getattr(result, "sources", None):
            parts.append("\n**Sources:**")
            for i, src in enumerate(result.sources, 1):
                parts.append(f"- [{i}] {src}")

        if self.config.verbose and hasattr(result, "total_time"):
            parts.append(f"\n*Response time: {result.total_time}ms*")

        return "\n".join(parts)

    def _update_context(self, query: str, answer: str) -> None:
        # Keep minimal info to avoid leaking long content
        self.context_history.append(
            ChatMessage(role="user", content=f"Previous query: {query[:200]}")
        )
        # Trim history
        limit = self.config.max_context_messages
        if len(self.context_history) > limit:
            self.context_history = self.context_history[-limit:]

    # Optional convenience methods (not used by CrewAI directly)
    def check_balance(self) -> Dict[str, Any]:
        try:
            balance = self.client.balance()
            return {
                "available_credits": balance.available_credits,
                "status": "active" if balance.available_credits > 0 else "depleted",
            }
        except AISearchAPIError as e:
            return {"error": e.description, "status": "error"}

    def clear_context(self) -> None:
        self.context_history = []
        if self.config.verbose:
            print("[AI Search] Context history cleared")


# -----------------------------
# Convenience factory (optional)
# -----------------------------
def aisearch_tool(
    api_key: Optional[str] = None,
    config: Optional[AISearchToolConfig] = None
) -> AISearchTool:
    """
    Return an AISearchTool instance (so you can do tools=[aisearch_tool(...)] )
    """
    return AISearchTool(api_key=api_key, config=config)
