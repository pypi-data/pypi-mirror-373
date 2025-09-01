from typing import Any, Iterable, List, Optional, Union, Dict
import os

# Import your client types
# Your client exposes ChatMessage in its package (per your examples).
from aisearchapi_client import ChatMessage  # type: ignore


def env_api_key() -> str:
    """
    Get API key from env. You can rename the var if you use a different one.
    """
    key = (
        os.getenv("AISEARCH_API_KEY")
        or os.getenv("AIS_API_KEY")
        or os.getenv("AI_SEARCH_API_KEY")
    )
    if not key:
        raise ValueError(
            "Missing API key. Set AISEARCH_API_KEY (or pass api_key= to AISearchTool)."
        )
    return key


def to_chat_messages(
    context: Optional[
        Union[
            str,
            ChatMessage,
            Dict[str, Any],
            Iterable[Union[str, ChatMessage, Dict[str, Any], Iterable[str]]],
        ]
    ]
) -> Optional[List[ChatMessage]]:
    """
    Normalize many forms of context to a list[ChatMessage].

    Accepted input:
    - None
    - "single string"
    - ChatMessage
    - {"role": "user|assistant|system", "content": "..."}
    - [ ... any mix of the above ... ]
    - [("user", "text"), ("assistant", "text")]  # tuple/list pairs also ok

    Returns None or a non-empty list of ChatMessage.
    """
    if context is None:
        return None

    # Make it iterable
    if isinstance(context, (str, ChatMessage, dict)):
        items: Iterable = [context]  # type: ignore[assignment]
    else:
        items = context  # already iterable

    out: List[ChatMessage] = []
    for item in items:
        if isinstance(item, ChatMessage):
            out.append(item)
        elif isinstance(item, str):
            out.append(ChatMessage(role="user", content=item))
        elif isinstance(item, dict):
            role = str(item.get("role", "user"))
            content = str(item.get("content", ""))
            if content:
                out.append(ChatMessage(role=role, content=content))
        elif isinstance(item, (tuple, list)) and len(item) >= 1:
            # ("user","hello") or ["hello"]
            if len(item) == 1:
                role, content = "user", str(item[0])
            else:
                role, content = str(item[0]), str(item[1])
            if content:
                out.append(ChatMessage(role=role, content=content))
        else:
            # fallback: stringify
            out.append(ChatMessage(role="user", content=str(item)))

    return out or None


def format_sources(sources: Optional[Any]) -> str:
    """
    Make a readable sources list from many possible shapes.
    """
    if not sources:
        return ""
    lines: List[str] = []
    for s in sources:
        if isinstance(s, str):
            lines.append(f"- {s}")
        elif isinstance(s, dict):
            title = s.get("title") or s.get("name") or s.get("source") or ""
            url = s.get("url") or s.get("link") or ""
            if title and url and title != url:
                lines.append(f"- {title} — {url}")
            elif url:
                lines.append(f"- {url}")
            elif title:
                lines.append(f"- {title}")
        else:
            lines.append(f"- {s}")
    return "\n".join(lines)
