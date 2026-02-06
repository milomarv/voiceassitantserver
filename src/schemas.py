import uuid

from pydantic import BaseModel, Field, field_validator

from .services.persona.persona_service import PersonaService


class BaseSchema(BaseModel):
    class Config:
        extra = "forbid"


class PersonaSoundsSchema(BaseSchema):
    awake: str = Field(..., description="Path to the awake sound file")
    waiting: str = Field(..., description="Path to the waiting sound file")
    sleep: str = Field(..., description="Path to the sleep sound file")
    error: str = Field(..., description="Path to the error sound file")


class PersonaOutputSchema(BaseSchema):
    wake_words: list[str] = Field(..., description="List of available persona names and similar pronunciations")
    sounds: PersonaSoundsSchema = Field(..., description="Paths to the persona's sound files")


class AIInputSchema(BaseSchema):
    message: str = Field(..., description="User message to send to the AI")
    persona: str = Field(..., description="Name of the persona to use")
    session_id: str | None = Field(None, description="Optional session ID for conversation history")

    @field_validator("persona")
    @classmethod
    def validate_persona(cls, value: str) -> str:
        personas = PersonaService().list_names()
        if value not in personas:
            msg = f"Invalid persona: {value}. Allowed: {personas}"
            raise ValueError(msg)
        return value

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, value: str | None) -> str | None:
        if value is not None:
            try:
                uuid.UUID(value)
            except ValueError as e:
                raise ValueError("Invalid session_id format. Must be a valid UUID.") from e
        return value

    def is_empty_message(self) -> bool:
        return not self.message.strip()


class AIOutputSchema(BaseSchema):
    reply: str = Field(..., description="AI's reply message")
    session_id: str = Field(..., description="Session ID for conversation history")
    open_conversation: bool = Field(..., description="Indicates if the conversation is still open by a question")
