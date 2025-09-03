#PUSH

poetry version patch; poetry build; poetry publish

# Chatty Analytics

Models and custom classes to work across the Chattyverse.

Lastest update: 2024-11-07

## Development instrucions

1. Install poetry https://python-poetry.org/docs/
2. Run `poetry install`
3. Install with pymongo: poetry install -E db to include pymongo dependencies

## Architecture

### Models

- Data containers with Pydantic validation
- No business logic
- Little to no functionality (for that, see Services)
- Used for:
  - Request/response validation
  - Database document mapping
  - Cross-service data transfer
- Example:
  - `Message` model

### Services

- Contain all business logic
- Work with models
- Stateless
- Handle:
  - Object creation (factories)
  - Model specific functionality
- Example:
  - `MessageFactory`
    - Create a `Message` from webhook data
    - Create a `Message` from an agent request to send it to a chat
    - Instantiate a `Message` from data base information
    - Create a `Message` from a Chatty Response

## Implementation Status

✅ Implemented

### Models

- Base message models
  - DBMessage: Database message model
  - MessageRequest: It models the intent of a message to be sent to a chat, still not instantiated as ChattyMessage.
  - BaseMessage (abstract)
    - Subtypes: AudioMessage, DocumentMessage, ImageMessage, TextMessage, VideoMessage, etc.
- MetaNotificationJson: Models any notification from WhatsApp to the webhook
  - MetaMessageJson: Models the speicifc Notification with a messages object
  - MetaStatusJson: Models the specific Notification with a statuses object
  - MetaErrorJson: Models the specific Notification with an errors object
- ChattyResponse: Models a list of pre-set responses in Chatty, that will be instantiated as a ChattyMessage when sent to a chat.
- Auth0 company registrarion form model
- Event models
- Metrics models

### Services

- `MessageFactory`
  - Create a `Message` from webhook data
  - Create a `Message` from an agent request to send it to a chat
  - Instantiate a `Message` from data base information
  - Create a `Message` from a Chatty Response

🚧 In Progress

- Chat and its modules and services
- Service layer completion
- Company Assets

Chatty Analytics is a proprietary tool developed by Axel Gualda and the Chatty Team. This software is for internal use only and is not licensed for distribution or use outside of authorized contexts.

Copyright (c) 2024 Axel Gualda. All Rights Reserved.
