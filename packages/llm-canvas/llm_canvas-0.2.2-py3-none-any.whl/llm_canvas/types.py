"""Type definitions for llm_canvas.

This module contains all TypedDict definitions used throughout the llm_canvas package,
including API request/response types and core data structures.
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict, Union

try:
    from typing import NotRequired
except ImportError:
    from typing_extensions import NotRequired

from anthropic.types import ImageBlockParam, TextBlockParam, ToolResultBlockParam, ToolUseBlockParam

# ---- Core Data Types ----

# Union type for message blocks matching TypeScript
MessageBlock = Union[TextBlockParam, ToolUseBlockParam, ToolResultBlockParam, ImageBlockParam]


class Message(TypedDict):
    """Message structure for canvas conversations."""

    content: Union[str, list[MessageBlock]]
    role: Literal["user", "assistant", "system"]


class Position(TypedDict):
    """Position information for a message node."""

    x: float
    y: float


class Dimension(TypedDict):
    """Dimension information for a message node."""

    width: float
    height: float


class MessageNode(TypedDict):
    """Node in the canvas conversation graph."""

    id: str
    message: Message
    child_ids: list[str]
    parent_id: NotRequired[str]
    meta: NotRequired[dict[str, Any]]
    position: NotRequired[Position]
    dimension: NotRequired[Dimension]


class CanvasSummary(TypedDict):
    """Summary information about a canvas."""

    canvas_id: str
    created_at: float
    root_ids: list[str]
    node_count: int
    title: Union[str, None]
    description: Union[str, None]
    meta: dict[str, Any]


class CanvasData(TypedDict):
    """Complete canvas data structure."""

    title: Union[str, None]
    last_updated: Union[float, None]
    description: Union[str, None]
    canvas_id: str
    created_at: float
    nodes: dict[str, MessageNode]


CanvasEventType = Literal["commit_message", "update_message", "delete_message"]


class CanvasCommitMessageEvent(TypedDict):
    """Event data for canvas message commits."""

    event_type: Literal["commit_message"]
    canvas_id: str
    timestamp: float
    data: MessageNode


class CanvasUpdateMessageEvent(TypedDict):
    """Event data for canvas message updates."""

    event_type: Literal["update_message"]
    canvas_id: str
    timestamp: float
    data: MessageNode


class CanvasDeleteMessageEvent(TypedDict):
    """Event data for canvas message deletions."""

    event_type: Literal["delete_message"]
    canvas_id: str
    timestamp: float
    data: str  # Node ID that was deleted


CanvasEvent = Union[CanvasCommitMessageEvent, CanvasUpdateMessageEvent, CanvasDeleteMessageEvent]


class BranchInfo(TypedDict):
    """Information about a canvas branch."""

    name: str
    description: Union[str, None]
    head_node_id: Union[str, None]
    created_at: float
