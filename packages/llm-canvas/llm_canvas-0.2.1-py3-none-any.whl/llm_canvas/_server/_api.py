"""API endpoints for llm_canvas.

Provides API endpoints defined in doc/server/api.md:
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncGenerator
from typing import Literal, Union

from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from llm_canvas._server._types import SSEEvent
from llm_canvas.canvas import Canvas
from llm_canvas.types import (
    CanvasCommitMessageEvent,
    CanvasData,
    CanvasSummary,
    CanvasUpdateMessageEvent,
)

from ._events import create_sse_stream, get_event_dispatcher
from ._registry import get_local_registry

# ---- API Request BaseModel Definitions ----


class CreateCanvasRequest(BaseModel):
    """Request type for POST /api/v1/canvas"""

    title: Union[str, None] = None
    description: Union[str, None] = None


class UpdateCanvasRequest(BaseModel):
    """Request type for PUT /api/v1/canvas/{canvas_id}"""

    title: Union[str, None] = None
    description: Union[str, None] = None


class CommitMessageRequest(BaseModel):
    data: CanvasCommitMessageEvent


class UpdateMessageRequest(BaseModel):
    data: CanvasUpdateMessageEvent


# ---- API Response BaseModel Definitions ----


class HealthCheckResponse(BaseModel):
    """Response type for GET /api/v1/health"""

    status: Literal["healthy"]
    server_type: Literal["local", "cloud"]
    timestamp: Union[float, None]


class GetCanvasResponse(BaseModel):
    data: CanvasData


class ErrorResponse(BaseModel):
    """Standard error response format"""

    error: str
    message: str


class StreamEventData(BaseModel):
    """Data structure for SSE stream events"""

    event: str
    data: str


class CanvasListResponse(BaseModel):
    """Response type for GET /api/v1/canvas/list"""

    canvases: list[CanvasSummary]


class CreateCanvasResponse(BaseModel):
    """Response type for POST /api/v1/canvas"""

    canvas_id: str
    message: str


class DeleteCanvasResponse(BaseModel):
    """Response type for DELETE /api/v1/canvas/{canvas_id}"""

    canvas_id: str
    message: str


class CreateMessageResponse(BaseModel):
    """Response type for POST /api/v1/canvas/{canvas_id}/messages"""

    message_id: str
    canvas_id: str
    message: str


class DeleteMessageResponse(BaseModel):
    """Response type for DELETE /api/v1/canvas/{canvas_id}/messages/{message_id}"""

    message_id: str
    canvas_id: str
    message: str


class SSEDocumentationResponse(BaseModel):
    """Response type for GET /api/v1/sse/documentation"""

    events: list[SSEEvent]


logger = logging.getLogger(__name__)
registry = get_local_registry()
event_dispatcher = get_event_dispatcher()
API_PREFIX = "/api/v1"


v1_router = APIRouter(
    prefix=API_PREFIX,
    tags=["v1"],
)


# Add a health check endpoint
@v1_router.get("/health")
def health_check() -> HealthCheckResponse:
    """Health check endpoint to verify server is running."""
    return HealthCheckResponse(status="healthy", server_type="local", timestamp=None)


@v1_router.get("/sse/documentation")
def sse_documentation() -> SSEDocumentationResponse:
    """
    SSE documentation endpoint that describes available event types.

    You should never call this, this endpoint is to make openapi generator happy
    """

    return SSEDocumentationResponse(events=[])


@v1_router.get("/canvas/list")
def list_canvases() -> CanvasListResponse:
    """List all available canvases.
    Returns:
        CanvasListResponse with list of canvas summaries
    """
    items: list[CanvasSummary] = [c.to_summary() for c in registry.list()]
    return CanvasListResponse(canvases=items)


@v1_router.get("/canvas")
def get_canvas(canvas_id: str = Query(..., description="Canvas UUID")) -> GetCanvasResponse:
    """Get a full canvas by ID.
    Args:
        canvas_id: Canvas UUID to retrieve
    Returns:
        CanvasData on success
    Raises:
        HTTPException: 404 if canvas not found
    """
    logger.info(f"Fetching canvas {canvas_id}")
    c = registry.get(canvas_id)
    if not c:
        error_response = ErrorResponse(error="canvas_not_found", message="Canvas not found")
        raise HTTPException(
            status_code=404,
            detail=error_response.dict(),
        )

    return GetCanvasResponse(data=c.to_canvas_data())


@v1_router.post("/canvas")
async def create_canvas(request: CreateCanvasRequest) -> CreateCanvasResponse:
    """Create a new canvas.
    Args:
        request: Canvas creation request with optional title and description
    Returns:
        CreateCanvasResponse with the canvas ID and success message
    """

    canvas = Canvas(title=request.title, description=request.description)
    registry.add(canvas)
    logger.info(f"Created canvas {canvas.canvas_id}")

    # Trigger canvas created event
    await event_dispatcher.canvas_created(canvas.to_summary())

    return CreateCanvasResponse(canvas_id=canvas.canvas_id, message="Canvas created successfully")


@v1_router.delete("/canvas/{canvas_id}")
async def delete_canvas(canvas_id: str = Path(..., description="Canvas UUID to delete")) -> DeleteCanvasResponse:
    """Delete a canvas by ID.
    Args:
        canvas_id: Canvas UUID to delete
    Returns:
        DeleteCanvasResponse with success message
    Raises:
        HTTPException: 404 if canvas not found
    """
    removed = registry.remove(canvas_id)
    if not removed:
        error_response = ErrorResponse(error="canvas_not_found", message="Canvas not found")
        raise HTTPException(
            status_code=404,
            detail=error_response.dict(),
        )
    logger.info(f"Deleted canvas {canvas_id}")

    # Trigger canvas deleted event
    await event_dispatcher.canvas_deleted(canvas_id)

    return DeleteCanvasResponse(canvas_id=canvas_id, message="Canvas deleted successfully")


@v1_router.post("/canvas/{canvas_id}/messages")
async def commit_message(
    request: CommitMessageRequest,
    canvas_id: str = Path(..., description="Canvas UUID"),
) -> CreateMessageResponse:
    """Commit a new message to a canvas.
    Args:
        canvas_id: Canvas UUID to add message to
        request: Canvas commit message event data
    Returns:
        CreateMessageResponse with the message ID and success message
    Raises:
        HTTPException: 404 if canvas not found
    """
    canvas = registry.get(canvas_id)
    if not canvas:
        error_response = ErrorResponse(error="canvas_not_found", message="Canvas not found")
        raise HTTPException(
            status_code=404,
            detail=error_response.model_dump(),
        )
    node_data = request.data["data"]
    node_id = node_data["id"]
    # check if the node id already exist
    if canvas.get_node(node_id):
        error_response2 = ErrorResponse(error="node_already_exists", message="Node already exists")
        raise HTTPException(
            status_code=400,
            detail=error_response2.model_dump(),
        )
    # Commit the message to the canvas
    canvas.nodes[node_data["id"]] = node_data
    logger.info(f"Committed message {node_data['id']} to canvas {canvas_id}")

    # Trigger message committed event
    await event_dispatcher.message_committed(canvas_id, node_data)

    return CreateMessageResponse(
        message_id=node_data["id"],
        canvas_id=canvas_id,
        message="Message committed successfully",
    )


@v1_router.put("/canvas/{canvas_id}/messages/{message_id}")
async def update_message(
    request: UpdateMessageRequest,
    canvas_id: str = Path(..., description="Canvas UUID"),
    message_id: str = Path(..., description="Message ID to update"),
) -> CreateMessageResponse:
    """Update an existing message in a canvas.
    Args:
        canvas_id: Canvas UUID containing the message
        message_id: Message ID to update
        request: Canvas update message event data
    Returns:
        CreateMessageResponse with the message ID and success message
    Raises:
        HTTPException: 404 if canvas or message not found
    """

    canvas = registry.get(canvas_id)
    if not canvas:
        error_response = ErrorResponse(error="canvas_not_found", message="Canvas not found")
        raise HTTPException(
            status_code=404,
            detail=error_response.dict(),
        )
    # Check if message exists
    if canvas.get_node(message_id) is None:
        error_response2 = ErrorResponse(error="message_not_found", message="Message not found")
        raise HTTPException(
            status_code=404,
            detail=error_response2.dict(),
        )
    # Extract message data from the event
    node_data = request.data["data"]
    # Update the message in the canvas
    canvas.update_message(message_id, node_data)
    logger.info(f"Updated message {message_id} in canvas {canvas_id}")

    # Trigger message updated event
    await event_dispatcher.message_updated(canvas_id, node_data)

    return CreateMessageResponse(
        message_id=message_id,
        canvas_id=canvas_id,
        message="Message updated successfully",
    )


# ---- SSE Endpoints ----
@v1_router.get("/canvas/sse")
async def canvas_sse() -> StreamingResponse:
    """Server-Sent Events endpoint for global canvas updates.

    Sends events when canvases are created, updated, or deleted.
    Events include:
    - canvas_created: When a new canvas is created
    - canvas_updated: When a canvas is updated
    - canvas_deleted: When a canvas is deleted

    Returns:
        StreamingResponse with SSE events
    """
    queue: asyncio.Queue[str] = asyncio.Queue(maxsize=100)

    # Add connection to global event dispatcher
    await event_dispatcher.add_global_connection(queue)

    async def cleanup() -> None:
        await event_dispatcher.remove_global_connection(queue)

    # Create the SSE stream
    stream = create_sse_stream(queue)

    # Wrap the stream to handle cleanup
    async def wrapped_stream() -> AsyncGenerator[str, None]:
        try:
            async for chunk in stream:
                logger.info(f"Sending SSE chunk: {chunk.strip()}")
                yield chunk
        except asyncio.CancelledError:
            logger.info("SSE global stream cancelled by client")
            raise
        except Exception:
            logger.exception("Error in SSE global stream")
        finally:
            await cleanup()

    return StreamingResponse(
        wrapped_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@v1_router.get("/canvas/{canvas_id}/sse")
async def canvas_message_sse(canvas_id: str = Path(..., description="Canvas UUID")) -> StreamingResponse:
    """Server-Sent Events endpoint for canvas message updates.

    Sends events when messages are added, updated, or deleted in a specific canvas.
    Events include:
    - message_committed: When a new message is added to the canvas
    - message_updated: When an existing message is updated
    - message_deleted: When a message is deleted

    Args:
        canvas_id: Canvas UUID to stream events for
    Returns:
        StreamingResponse with SSE events
    Raises:
        HTTPException: 404 if canvas not found
    """
    # Verify canvas exists
    canvas = registry.get(canvas_id)
    if not canvas:
        error_response = ErrorResponse(error="canvas_not_found", message="Canvas not found")
        raise HTTPException(
            status_code=404,
            detail=error_response.dict(),
        )

    queue: asyncio.Queue[str] = asyncio.Queue(maxsize=100)

    # Add connection to canvas-specific event dispatcher
    await event_dispatcher.add_canvas_connection(canvas_id, queue)

    async def cleanup() -> None:
        await event_dispatcher.remove_canvas_connection(canvas_id, queue)

    # Create the SSE stream
    stream = create_sse_stream(queue)

    # Wrap the stream to handle cleanup
    async def wrapped_stream() -> AsyncGenerator[str, None]:
        try:
            async for chunk in stream:
                yield chunk
        except asyncio.CancelledError:
            logger.info(f"SSE canvas stream for {canvas_id} cancelled by client")
            raise
        except Exception:
            logger.exception(f"Error in SSE canvas stream for {canvas_id}")
        finally:
            await cleanup()

    return StreamingResponse(
        wrapped_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
