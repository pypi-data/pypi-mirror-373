from typing import Any, List, Optional, Type, Union, Dict
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

# Your Python client
from aisearchapi_client import AISearchAPIClient, AISearchAPIError  # type: ignore

from .utils import env_api_key, to_chat_messages, format_sources


class AISearchInput(BaseModel):
    prompt: str = Field(..., description="Main user question.")
    response_type: Optional[str] = Field(
        default="markdown",
        description="Response type: 'markdown' or 'text'.",
    )
    # accept one OR many messages
    context: Optional[
        Union[
            str,
            Dict[str, Any],
            List[Union[str, Dict[str, Any]]],
        ]
    ] = Field(
        default=None,
        description=(
            "Optional extra context. Can be a string or a list of messages. "
            "Each message can be a string or an object like "
            '{"role":"user|assistant|system","content":"..."}'
        ),
    )


class AISearchTool(BaseTool):
    name: str = "AI Search (semantic)"
    description: str = (
        "Use this tool to search the web semantically and get answers with sources."
    )
    args_schema: Type[BaseModel] = AISearchInput

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ):
        super().__init__()
        self._client = AISearchAPIClient(
            api_key=api_key or env_api_key(),
            base_url=base_url or "https://api.aisearchapi.io",
            timeout=timeout,
        )

    # CrewAI calls _run with validated args
    def _run(
        self,
        prompt: str,
        response_type: Optional[str] = "markdown",
        context: Optional[Union[str, Dict[str, Any], List[Union[str, Dict[str, Any]]]]] = None,
    ) -> str:
        try:
            msgs = to_chat_messages(context)
            result = self._client.search(
                prompt=prompt,
                context=msgs,
                response_type=response_type or "markdown",
            )
            answer = getattr(result, "answer", "")
            sources = getattr(result, "sources", None)
            src_text = format_sources(sources)
            if src_text:
                return f"{answer}\n\nSources:\n{src_text}"
            return answer or "No answer."
        except AISearchAPIError as e:
            return f"AI Search API error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"

    async def _arun(
        self,
        prompt: str,
        response_type: Optional[str] = "markdown",
        context: Optional[Union[str, Dict[str, Any], List[Union[str, Dict[str, Any]]]]] = None,
    ) -> str:
        # Simple async wrapper
        return self._run(prompt=prompt, response_type=response_type, context=context)
