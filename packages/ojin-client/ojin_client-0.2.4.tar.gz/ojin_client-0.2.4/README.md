# Ojin Persona Client

A WebSocket client for Ojin Persona model that handles communication with Inference Server. It is used for example by Ojin Persona Service for Pipecat https://github.com/pipecat-ai/pipecat

## Requirements

- Python 3.10+
- pip or uv package manager

## Installation

```bash
pip install ojin-client
```

### Usage

```python
from ojin.ojin_persona_client import OjinPersonaClient

avatar = OjinPersonaClient(
        ws_url="THE_OJIN_URL",
        api_key="YOUR_OJIN_API_KEY",
        avatar_config_id="YOUR_OJIN_CONFIGURATION"M
    )
```

### API methods

- connect: Establishes the websocket connection with the ojin inference server
- start_interaction: Creates a UUID to send in the interaction messages
- send_message: Sends messages to the ojin inference server
- receive_message: Receives messages from the ojin inference server
- close: closes the connection with ojin inference server

### Messages

- OjinPersonaInteractionReadyMessage: Message indicating that an interaction is ready to begin

- OjinPersonaSessionReadyMessage: Message to start a new interaction with an Ojin Persona

- OjinPersonaCancelInteractionMessage: Message to cancel an interaction

- OjinPersonaInteractionInputMessage: Contains the audio data as bytes and a flag indicating if this is the last input

### Responses

- StartInteractionResponseMessage: Response message for a successful interaction start

- OjinPersonaInteractionResponseMessage: Response message containing video data from the avatar

- ErrorResponseMessage: Response message informing the client there was an error
