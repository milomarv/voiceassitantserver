import datetime as dt
import uuid

from pydantic import BaseModel, field_validator, model_validator

from ._base_service import BaseService
from .persona._base_persona import BasePersona

OPEN_CONVERSATION_INDICATORS = [
    "?",
    "Wenn du möchtest",
    "Wenn du mehr wissen",
    "Ich bitte dich",
    "Ich höre zu",
]


class HistoryMessage(BaseModel):
    role: str
    content: str
    open_conversation: bool = False

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        allowed_roles = {"system", "user", "assistant"}
        if value not in allowed_roles:
            msg = f"Invalid role: '{value}'. Allowed roles: {allowed_roles}"
            raise ValueError(msg)
        return value

    @model_validator(mode="before")
    @classmethod
    def set_reply_flag(cls, values: dict) -> dict:
        content = values.get("content", "")
        if content:
            cutoff = int(len(content) * 0.7)
            tail = content[cutoff:]
        else:
            tail = ""

        values["open_conversation"] = any(indicator in tail for indicator in OPEN_CONVERSATION_INDICATORS)
        return values


class HistorySession:
    def __init__(self, session_id: str, persona: BasePersona, max_turns: int) -> None:
        self.session_id: str = session_id
        self.persona: BasePersona = persona
        self.max_turns: int = max_turns

        self.last_update: dt.datetime = None
        self.messages: list[HistoryMessage] = []
        self.system_message: HistoryMessage = HistoryMessage(role="system", content=persona.system_prompt)

        self.set_last_update_to_now()

    def _update(method: callable) -> callable:  # noqa: N805
        def wrapper(self: "HistorySession", *args, **kwargs) -> None:
            try:
                return method(self, *args, **kwargs)
            finally:
                self.set_last_update_to_now()

        return wrapper

    def _cleanup(method: callable) -> callable:  # noqa: N805
        def wrapper(self: "HistorySession", *args, **kwargs) -> None:
            result = method(self, *args, **kwargs)
            self._cleanup_max_turns()
            return result

        return wrapper

    def _cleanup_max_turns(self) -> None:
        max_messages = self.max_turns * 2
        if len(self.messages) > max_messages:
            if self.messages[0].role == "system":
                self.system_message = self.messages[0]
            self.messages = self.messages[-max_messages:]

    @_update
    @_cleanup
    def _add_message(self, role: str, content: str) -> None:
        message = HistoryMessage(role=role, content=content)
        self.messages.append(message)

    def set_last_update_to_now(self) -> None:
        self.last_update = dt.datetime.now(tz=dt.UTC)

    def add_user_message(self, content: str) -> None:
        self._add_message(role="user", content=content)

    def add_assistant_message(self, content: str) -> None:
        self._add_message(role="assistant", content=content)

    def update_system_prompt(self, new_prompt: str) -> None:
        new_prompt = "DU bist jetzt eine andere Persönlichkeit:\n" + new_prompt
        self._add_message(role="system", content=new_prompt)

    def get_last_assistant_message(self) -> str | None:
        for message in reversed(self.messages):
            if message.role == "assistant":
                return message.content
        return None

    def check_for_open_conversation(self) -> bool:
        last_message = self.messages[-1] if self.messages else None
        return bool(last_message and last_message.open_conversation)

    def dump_for_openai(self) -> list[dict[str, str]]:
        history_json = [self.system_message.model_dump()]
        history_json.extend([msg.model_dump() for msg in self.messages])
        for msg in history_json:
            del msg["open_conversation"]
        return history_json


class HistoryService(BaseService):
    def __init__(self) -> None:
        super().__init__("History")
        self.cache: list[HistorySession] = []
        self.cleanup_seconds: int = self.settings.HISTORY_CLEANUP_SECONDS

    def _cleanup_cache(mehod: callable) -> callable:  # noqa: N805
        def wrapper(self: "HistoryService", *args, **kwargs) -> None:
            for session in self.cache:
                if (dt.datetime.now(tz=dt.UTC) - session.last_update).total_seconds() > self.cleanup_seconds:
                    self.logger.info(f"Cleaning up session: '{session.session_id}'")
                    self.cache.remove(session)
            return mehod(self, *args, **kwargs)

        return wrapper

    @_cleanup_cache
    def get_session(self, session_id: str, persona: BasePersona) -> HistorySession | None:
        for session in self.cache:
            if session.session_id == session_id:
                self.logger.info(f"Retrieved session: '{session_id}'")

                if session.persona.name != persona.name:
                    self.logger.info(
                        f"Session persona '{session.persona.name}' does not match requested persona '{persona.name}'. Updating session persona.",  # noqa: E501
                    )
                    session.persona = persona
                    session.update_system_prompt(persona.system_prompt)
                return session
        self.logger.warning(f"Session not found: '{session_id}'")
        return None

    @_cleanup_cache
    def register_session(self, persona: BasePersona) -> HistorySession:
        session_id = str(uuid.uuid4())
        session = HistorySession(
            session_id=session_id,
            persona=persona,
            max_turns=self.settings.HISTORY_MAX_TURNS,
        )
        self.cache.append(session)
        self.logger.info(f"Registered new session: '{session_id}'")
        return session
