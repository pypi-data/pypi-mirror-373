"""Entities for session messages."""

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Enum for WebSocket message types."""

    # Client -> Proxy Messages
    INTERACTION_INPUT = "interactionInput"
    CANCEL_INTERACTION = "cancelInteraction"
    SESSION_UPDATE = "sessionUpdate"

    # Proxy -> Client Messages
    SESSION_READY = "sessionReady"
    INTERACTION_RESPONSE = "interactionResponse"
    ERROR_RESPONSE = "errorResponse"

    # Proxy -> Inference Server Messages
    SESSION_SETUP = "sessionSetup"


class SessionSetupPayload(BaseModel):
    """Payload for session setup messages."""

    model_id: str = Field(..., description="Identifier for the target inference model")
    trace_id: str = Field(..., description="Identifier for the session")
    parameters: Optional[Dict[str, Any]] = Field(
        None, description="Optional model-specific parameters (key-value pairs)"
    )
    timestamp: Optional[int] = Field(
        None,
        description="Timestamp in milliseconds when the message was sent by the client",
    )


class SessionUpdatePayload(BaseModel):
    """Payload for session update messages."""

    parameters: Optional[Dict[str, Any]] = Field(
        None, description="Updated model-specific parameters"
    )
    timestamp: Optional[int] = Field(
        None,
        description="Timestamp in milliseconds when the message was sent by the client",
    )


class SessionReadyPayload(BaseModel):
    """Payload for session ready messages."""

    trace_id: str = Field(
        ...,
        description="Unique identifier assigned to this WebSocket session by the proxy",
    )
    status: str = Field("success", description="Indicates successful setup")
    load: float = Field(..., description="The current server load")
    timestamp: Optional[int] = Field(
        None,
        description="Timestamp in milliseconds when the message was sent by the proxy",
    )


class SessionSetupMessage(BaseModel):
    """Session setup message sent from client to proxy."""

    type: MessageType = MessageType.SESSION_SETUP
    payload: SessionSetupPayload


class SessionUpdateMessage(BaseModel):
    """Session update message sent from client to proxy."""

    type: MessageType = MessageType.SESSION_UPDATE
    payload: SessionUpdatePayload


class SessionReadyMessage(BaseModel):
    """Session ready message sent from proxy to client."""

    type: MessageType = MessageType.SESSION_READY
    payload: SessionReadyPayload
