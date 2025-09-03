"""
Markdown-Flow LLM Integration Module

Provides LLM provider interfaces and related data models, supporting multiple processing modes.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional

from .constants import NO_LLM_PROVIDER_ERROR


class ProcessMode(Enum):
    """LLM processing modes."""

    PROMPT_ONLY = "prompt_only"  # Return prompt only, no LLM call
    COMPLETE = "complete"  # Complete processing (non-streaming)
    STREAM = "stream"  # Streaming processing


@dataclass
class LLMResult:
    """Unified LLM processing result."""

    content: str = ""  # Final content
    prompt: Optional[str] = None  # Used prompt
    variables: Optional[Dict[str, str]] = None  # Extracted variables
    metadata: Optional[Dict[str, Any]] = None  # Metadata

    def __bool__(self):
        """Support boolean evaluation."""
        return bool(self.content or self.prompt or self.variables)


class LLMProvider(ABC):
    """Abstract LLM provider interface."""

    @abstractmethod
    async def complete(self, messages: List[Dict[str, str]]) -> str:
        """
        Non-streaming LLM call.

        Args:
            messages: Message list in format [{"role": "system/user/assistant", "content": "..."}]

        Returns:
            str: LLM response content

        Raises:
            ValueError: When LLM call fails
        """
        pass

    @abstractmethod
    async def stream(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """
        Streaming LLM call.

        Args:
            messages: Message list in format [{"role": "system/user/assistant", "content": "..."}]

        Yields:
            str: Incremental LLM response content

        Raises:
            ValueError: When LLM call fails
        """
        pass


class NoLLMProvider(LLMProvider):
    """Empty LLM provider for prompt-only scenarios."""

    async def complete(self, messages: List[Dict[str, str]]) -> str:
        raise NotImplementedError(NO_LLM_PROVIDER_ERROR)

    async def stream(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        raise NotImplementedError(NO_LLM_PROVIDER_ERROR)
        yield ""  # pragma: no cover
