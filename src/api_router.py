from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from depends import Logger

from .schemas import AIInputSchema, AIOutputSchema, PersonaOutputSchema, PersonaSoundsSchema
from .services.ai_service import AIService
from .services.history_service import HistoryService
from .services.persona.persona_service import PersonaService

logger = Logger("Router")
router = APIRouter()
persona_service = PersonaService()
history_service = HistoryService()
ai_service = AIService()


@router.get("/health")
def health_check() -> dict:
    logger.info("Health check requested.")
    return {"status": "ok"}


@router.get("/persona")
def list_personas() -> dict[str, PersonaOutputSchema]:
    names = []
    output = {}
    for persona in persona_service.list_personas():
        names.append(persona.name)
        output[persona.name] = PersonaOutputSchema(
            wake_words=persona.wake_words,
            sounds=PersonaSoundsSchema(
                awake=persona.sounds.awake,
                waiting=persona.sounds.waiting,
                sleep=persona.sounds.sleep,
                error=persona.sounds.error,
            ),
        )
    logger.info(f"Retrieved personas. Available: {names}")
    return output


@router.post("/ai")
def send_to_ai(payload: AIInputSchema) -> AIOutputSchema:
    logger.info(f"Received payload: {payload.model_dump_json()}")

    try:
        if payload.is_empty_message():
            logger.warning("Received empty message.")
            return AIOutputSchema(
                reply="Tut mir leid, aber das habe ich nicht verstanden. Kannst du es bitte erneut versuchen?",
                session_id=payload.session_id or "",
            )

        persona = persona_service.get_persona(payload.persona)

        history_session = history_service.get_session(payload.session_id or "", persona=persona)
        if history_session is None:
            history_session = history_service.register_session(persona=persona)

        history_session.add_user_message(payload.message)
        history_session = ai_service.extend_history(history_session)

        return AIOutputSchema(
            reply=history_session.get_last_assistant_message() or "Ich kann dir im Moment nicht antworten.",
            session_id=history_session.session_id,
            open_conversation=history_session.check_for_open_conversation(),
        )

    except Exception as e:
        error_type = type(e).__name__
        logger.exception(f"Unexpected error: {e!s}")
        return AIOutputSchema(
            reply=f"Es ist ein Fehler des Typs {error_type} aufgetreten. Bitte versuche es später erneut.",
            session_id=payload.session_id or "",
            open_conversation=False,
        )


@router.get("/sound/{path:path}")
def download_sound(path: str) -> dict:
    file_path = f"./sounds/{path}.mp3"
    logger.info(f"Sound requested: {file_path}")

    # Check if file exists
    if not Path(file_path).is_file():
        raise HTTPException(status_code=404, detail="Sound file not found")

    return FileResponse(file_path, media_type="audio/mpeg")
