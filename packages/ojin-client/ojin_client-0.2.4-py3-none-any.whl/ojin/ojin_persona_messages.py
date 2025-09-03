"""OJIN Persona message definitions and handlers.

This module contains message classes and utilities for handling communication
with the OJIN Persona service, including audio input messages, cancellation
messages, and video response messages.
"""
import base64
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from deprecated import deprecated
from pydantic import BaseModel, Field

from ojin.entities.interaction_messages import (
    CancelInteractionInput,
    InteractionInput,
    InteractionInputMessage,
    InteractionResponseMessage,
)


class OjinPersonaMessage(BaseModel):
    """Base class for all Ojin Persona messages.

    All messages exchanged with the Ojin Persona backend inherit from this class.
    """

    def to_proxy_message(self) -> BaseModel:
        """Convert the message to a proxy message format.
   
        This method must be implemented by subclasses to define how the specific
        message type should be converted to its corresponding proxy message format.
   
        Returns:
        BaseModel: The proxy message representation of this message.
       
        Raises:
        NotImplementedError: Always raised as this method must be implemented
                          by concrete subclasses.

        """
        raise NotImplementedError


class OjinPersonaSessionReadyMessage(OjinPersonaMessage):
    """Message to start a new interaction with an Ojin Persona.

    Contains the ID of the persona to interact with.
    """

class OjinPersonaSessionReadyPing(OjinPersonaMessage):
    """Ping message used to check session readiness with the Ojin Persona backend."""


@deprecated(version='0.2.0', reason="Use start_interaction method instead")
class StartInteractionMessage(OjinPersonaMessage):
    """DEPRECATED: Message to start a new interaction with an Ojin Persona.

    Contains the ID of the persona to interact with.
    """


class StartInteractionResponseMessage(OjinPersonaMessage):
    """Response message for a successful interaction start.

    Contains the unique ID assigned to the new interaction.
    """

    interaction_id: str


class OjinPersonaInteractionReadyMessage(OjinPersonaMessage):
    """Message indicating that an interaction is ready to begin.

    Contains the interaction ID and persona ID.
    """

    interaction_id: str


class OjinPersonaInteractionResponseMessage(OjinPersonaMessage):
    """Response message containing video data from the persona.

    Contains the interaction ID, persona ID, and the video data as bytes.
    """

    interaction_id: str
    video_frame_bytes: bytes
    is_final_response: bool = False

    @classmethod
    def from_proxy_message(cls, proxy_message: InteractionResponseMessage):
        """Create an instance from a proxy message response.
   
        Extracts video frame data and metadata from an InteractionResponseMessage
        to construct a new instance of this class.
   
        Args:
        proxy_message (InteractionResponseMessage): The proxy message containing
                                                  interaction response data with
                                                  video payload and metadata.
   
        Returns:
        cls: A new instance created from the proxy message data, containing
            the interaction ID, video frame bytes, and final response flag.

        """
        return cls(
            interaction_id=proxy_message.payload.interaction_id,
            video_frame_bytes=proxy_message.payload.payload,
            is_final_response=proxy_message.payload.is_final_response,
        )


class OjinPersonaCancelInteractionMessage(OjinPersonaMessage):
    """Message to cancel an interaction."""

    interaction_id: str

    def to_proxy_message(self) -> CancelInteractionInput:
        """Convert the cancel message to a proxy message format.
   
        Creates a CancelInteractionInput message with the interaction ID and
        current timestamp to request cancellation of an ongoing interaction.
           
        Returns:
            CancelInteractionInput: A cancellation message containing the
                                   interaction ID and timestamp for the proxy
                                   service to process the cancellation request.

        """
        return CancelInteractionInput(
            interaction_id=self.interaction_id,
            timestamp=int(time.monotonic() * 1000),
        )


class OjinPersonaInteractionInputMessage(OjinPersonaMessage):
    """Message containing audio input for the persona.

    Contains the audio data as bytes and a flag indicating if this is the last input.
    """

    audio_int16_bytes: bytes
    interaction_id: str = Field(default="", init=True)
    params: Optional[Dict[str, Any]] = Field(default=None, init=True)
    is_last_input: bool = Field(default=False, init=True)

    def to_proxy_message(self) -> BaseModel:
        """Convert the audio message to a proxy message format.
   
        Creates an InteractionInputMessage containing audio data encoded as base64,
        along with metadata such as interaction ID, timing information, and optional
        frame parameters.
   
        Returns:
        BaseModel: An InteractionInputMessage instance containing the encoded
                 audio data and associated metadata for transmission to the
                 proxy service.

        """        
        payload = InteractionInput(
            interaction_id=self.interaction_id,
            payload_type="audio",
            payload=base64.b64encode(self.audio_int16_bytes).decode("utf-8"),
            is_final_input=self.is_last_input,
            timestamp=int(time.monotonic() * 1000),
            params=self.params,
        )
        return InteractionInputMessage(
            payload=payload,
        )



class IOjinPersonaClient(ABC):
    """Interface for Ojin Persona client communication.

    Defines the contract for sending and receiving messages to/from the Ojin Persona
    client.
    """

    @abstractmethod
    async def connect(self) -> None:
        """Connect the client to the proxy."""

    @abstractmethod
    async def send_message(self, message: BaseModel) -> None:
        """Send a message to the server.

        Args:
           message: The message to send.

        """

    @abstractmethod 
    async def start_interaction(self) -> StartInteractionResponseMessage:
        """Create a UUID for server interactions.

        Returns:
            The UUID.

        """

    @abstractmethod
    async def receive_message(self) -> BaseModel|None:
        """Receive a message from the server.

        Returns:
            The received message.

        """

    @abstractmethod
    async def close(self) -> None:
        """Close the client."""
