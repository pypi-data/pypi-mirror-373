"""Interaction messages."""

import json
import struct
import uuid
from contextlib import suppress
from enum import IntEnum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from ojin.entities.session_messages import MessageType

# Message type constants for binary serialization
MESSAGE_TYPE_INTERACTION_INPUT = 0
MESSAGE_TYPE_INTERACTION_INPUT_FINAL = 1
MESSAGE_TYPE_INTERACTION_RESPONSE = 2
MESSAGE_TYPE_INTERACTION_RESPONSE_FINAL = 3

# Size of the fixed-size header in bytes
INTERACTION_INPUT_MESSAGE_HEADER_SIZE = 26
INTERACTION_RESPONSE_MESSAGE_HEADER_SIZE = 34

# Maximum size of params in bytes (must fit in one byte)
MAX_INTERACTION_PARAMS_SIZE = 255


class PayloadType(IntEnum):
    """Payload type constants for binary serialization."""

    TEXT = 0
    AUDIO = 1
    IMAGE = 2
    VIDEO = 3


def payload_type_from_str(payload_type_str: str):
    payload_type_map = {
        "text": PayloadType.TEXT,
        "audio": PayloadType.AUDIO,
        "image": PayloadType.IMAGE,
        "video": PayloadType.VIDEO,
    }
    return payload_type_map.get(payload_type_str.lower(), PayloadType.TEXT)


def payload_type_to_str(payload_type: PayloadType):
    payload_type_map = {
        PayloadType.TEXT: "text",
        PayloadType.AUDIO: "audio",
        PayloadType.IMAGE: "image",
        PayloadType.VIDEO: "video",
    }
    return payload_type_map.get(payload_type, "text")


class InteractionInput(BaseModel):
    """Interaction input."""

    interaction_id: str = Field(
        ...,
        description="Client ID linking messages for a single logical interaction",
    )
    payload_type: str = Field(
        ...,
        description="Type of the data in the payload",
    )
    payload: bytes = Field(
        ...,
        description="The actual data.",
    )
    is_final_input: bool = Field(
        ...,
        description="True if this is the last input chunk for this interaction",
    )
    params: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional. Additional parameters for the interaction",
    )
    timestamp: int = Field(
        ...,
        description="Timestamp (ms since Unix epoch) when message was sent by client",
    )


class CancelInteractionInput(BaseModel):
    interaction_id: str = Field(
        ...,
        description="ID linking this response to the corresponding client interaction",
    )

    timestamp: Optional[int] = Field(
        None,
        description="Timestamp in milliseconds when the message was sent by the proxy",
    )


class CancelInteractionMessage(BaseModel):
    """Interaction cancel message sent from client to proxy."""

    type: MessageType = MessageType.CANCEL_INTERACTION

    payload: CancelInteractionInput


class InteractionResponse(BaseModel):
    """Interaction response."""

    interaction_id: str = Field(
        ...,
        description="ID linking this response to the corresponding client interaction",
    )
    payload_type: str = Field(
        ...,
        description="Type of the data in the payload",
    )
    payload: bytes = Field(
        ...,
        description="The actual output data.",
    )
    is_final_response: bool = Field(
        ...,
        description="True if this is the final output chunk for this interaction_id",
    )
    timestamp: int = Field(
        ...,
        description="Timestamp (ms since Unix epoch) when message was sent by proxy",
    )
    usage: int = Field(
        ...,
        description="Usage metric for this response (unsigned 4-byte integer)",
    )
    index: int = Field(
        ...,
        description="The index of the inferred payload (e.g frame index in case of persona)",
    )


class ErrorResponse(BaseModel):
    """Error response."""

    interaction_id: Optional[str] = Field(
        None,
        description="Optional. The interaction_id related to the error, if applicable",
    )
    code: str = Field(
        ...,
        description="Short error code (e.g., AUTH_FAILED, INVALID_MODEL_ID, TIMEOUT)",
    )
    message: str = Field(
        ...,
        description="A human-readable description of the error",
    )
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional. Additional structured details about the error",
    )
    timestamp: int = Field(
        ...,
        description="Timestamp (ms since Unix epoch) when message was sent by proxy",
    )


class InteractionInputMessage(BaseModel):
    """Interaction input message sent from client to proxy."""

    type: MessageType = MessageType.INTERACTION_INPUT
    payload: InteractionInput

    def to_bytes(self) -> bytes:
        """
        Convert the message to bytes.

        Binary format:
        - Byte - message type:
            0 - InteractionInput
            1 - InteractionInput with is_final_input
        - Byte - payload type:
            0 - text
            1 - audio
            2 - image
            3 - video
        - 16 bytes - interaction_id (UUID)
        - 8 bytes - timestamp (uint64, milliseconds since Unix epoch)
        - Remaining bytes - payload data
        """
        # Convert UUID string to bytes (16 bytes)
        interaction_id_bytes = uuid.UUID(self.payload.interaction_id).bytes

        # Get message type as int
        message_type = (
            MESSAGE_TYPE_INTERACTION_INPUT_FINAL
            if self.payload.is_final_input
            else MESSAGE_TYPE_INTERACTION_INPUT
        )

        # Get payload type as int
        payload_type = payload_type_from_str(self.payload.payload_type)

        # Use current timestamp if not provided
        timestamp = self.payload.timestamp or int(
            uuid.UUID(self.payload.interaction_id).time
        )

        # Pack the fixed-size header
        header = struct.pack(
            "!BB16sQ",  # Format: Byte, Byte, 16 bytes UUID, uint64
            message_type,
            int(payload_type),
            interaction_id_bytes,
            timestamp,
        )

        # Serialize params if present
        params_bytes = b""
        if self.payload.params:
            try:
                params_json = json.dumps(self.payload.params).encode("utf-8")
                # Limit params size to MAX_PARAMS_SIZE bytes (fits in one byte)
                if len(params_json) > MAX_INTERACTION_PARAMS_SIZE:
                    params_json = params_json[:MAX_INTERACTION_PARAMS_SIZE]
                params_bytes = bytes([len(params_json)]) + params_json
            except (TypeError, UnicodeEncodeError):
                # If params can't be encoded, use empty params
                params_bytes = bytes([0])
        else:
            # No params
            params_bytes = bytes([0])

        # Combine header, params, and payload
        return header + params_bytes + self.payload.payload

    @staticmethod
    def from_bytes(data: bytes) -> "InteractionInputMessage":
        """
        Convert bytes to an InteractionInputMessage.

        Binary format:
        - Byte - message type:
            0 - InteractionInput
            1 - InteractionInputFinal
        - Byte - payload type:
            0 - text
            1 - audio
            2 - image
            3 - video
        - 16 bytes - interaction_id (UUID)
        - 8 bytes - timestamp (uint64, ms since Unix epoch)
        - Remaining bytes - payload data
        """
        # Ensure we have at least the header
        if len(data) < INTERACTION_INPUT_MESSAGE_HEADER_SIZE:
            raise ValueError("Invalid data: message too short")

        # Extract header fields
        message_type = data[0]
        payload_type_int = data[1]
        interaction_id_bytes = data[2:18]
        timestamp = struct.unpack("!Q", data[18:26])[0]

        # Extract params if present
        params = None
        params_size = data[26]
        current_pos = 27

        if params_size > 0:
            params_bytes = data[current_pos : current_pos + params_size]
            with suppress(json.JSONDecodeError, UnicodeDecodeError):
                params = json.loads(params_bytes.decode("utf-8"))
            current_pos += params_size

        # The rest is payload
        payload_bytes = data[current_pos:]

        # Convert bytes to UUID string
        interaction_id = str(uuid.UUID(bytes=interaction_id_bytes))

        # Determine if this is a final message
        is_final_input = message_type == MESSAGE_TYPE_INTERACTION_INPUT_FINAL

        # Convert payload type int to string
        payload_type = payload_type_to_str(payload_type_int)

        # Create the interaction input
        interaction_input = InteractionInput(
            interaction_id=interaction_id,
            payload_type=payload_type,
            payload=payload_bytes,
            is_final_input=is_final_input,
            timestamp=timestamp,
            params=params,
        )

        # Return the message
        return InteractionInputMessage(payload=interaction_input)


class InteractionResponseMessage(BaseModel):
    """Interaction response message sent from proxy to client."""

    type: MessageType = MessageType.INTERACTION_RESPONSE
    payload: InteractionResponse

    def to_bytes(self) -> bytes:
        """
        Convert the message to bytes.

        Binary format:
        - Byte - message type:
            0 - InteractionResponse
            1 - InteractionResponse with is_final_response
        - Byte - payload type:
            0 - text
            1 - audio
            2 - image
            3 - video
        - 16 bytes - interaction_id (UUID)
        - 8 bytes - timestamp (uint64, milliseconds since Unix epoch)
        - 4 bytes - usage (uint32)
        - 4 bytes - message index (uint32)
        - Remaining bytes - payload data
        """
        # Convert UUID string to bytes (16 bytes)
        interaction_id_bytes = uuid.UUID(self.payload.interaction_id).bytes

        # Get message type as int
        message_type = (
            MESSAGE_TYPE_INTERACTION_RESPONSE_FINAL
            if self.payload.is_final_response
            else MESSAGE_TYPE_INTERACTION_RESPONSE
        )

        # Get payload type as int
        payload_type = payload_type_from_str(self.payload.payload_type)

        timestamp = self.payload.timestamp
        usage = self.payload.usage
        index = self.payload.index

        # Pack the fixed-size header
        header = struct.pack(
            "!BB16sQII",  # Format: Byte, Byte, 16b UUID, uint64 timestamp, uint32 usage, uint32 index
            message_type,
            int(payload_type),
            interaction_id_bytes,
            timestamp,
            usage,
            index,
        )

        # Combine header and payload
        return header + self.payload.payload

    @staticmethod
    def get_usage_from_bytes(data: bytes) -> int:
        """
        Get the usage from the bytes.

        Binary format:
        - 4 bytes - usage (uint32)
        """
        return struct.unpack("!I", data[26:30])[0]

    @staticmethod
    def from_bytes(data: bytes) -> "InteractionResponseMessage":
        """
        Convert bytes to an InteractionResponseMessage.

        Binary format:
        - Byte - message type:
            0 - InteractionResponse
            1 - InteractionResponseFinal
        - Byte - payload type:
            0 - text
            1 - audio
            2 - image
            3 - video
        - 16 bytes - interaction_id (UUID)
        - 8 bytes - timestamp (uint64, milliseconds since Unix epoch)
        - 4 bytes - usage (uint32)
        - 4 bytes - message index (uint32)
        - Remaining bytes - payload data
        """
        # Ensure we have at least the header
        if len(data) < INTERACTION_RESPONSE_MESSAGE_HEADER_SIZE:
            raise ValueError("Invalid data: message too short")

        # Extract header fields
        message_type = data[0]
        payload_type_int = data[1]
        interaction_id_bytes = data[2:18]
        timestamp = struct.unpack("!Q", data[18:26])[0]
        usage = struct.unpack("!I", data[26:30])[0]
        index = struct.unpack("!I", data[30:34])[0]
        payload_bytes = data[34:]

        # Convert bytes to UUID string
        interaction_id = str(uuid.UUID(bytes=interaction_id_bytes))

        # Determine if this is a final message
        is_final_response = message_type == MESSAGE_TYPE_INTERACTION_RESPONSE_FINAL

        # Convert payload type int to string
        payload_type = payload_type_to_str(payload_type_int)

        # Create the interaction response
        interaction_response = InteractionResponse(
            interaction_id=interaction_id,
            payload_type=payload_type,
            payload=payload_bytes,
            is_final_response=is_final_response,
            timestamp=timestamp,
            usage=usage,
            index=index,
        )

        # Return the message
        return InteractionResponseMessage(payload=interaction_response)


class ErrorResponseMessage(BaseModel):
    """Error response message sent from proxy to client."""

    type: MessageType = MessageType.ERROR_RESPONSE
    payload: ErrorResponse
