from openai import OpenAI

from src.services._base_service import BaseService
from src.services.history_service import HistorySession


class AIService(BaseService):
    def __init__(self) -> None:
        super().__init__("AI")
        self.client = OpenAI(api_key=self.settings.OPENAI_API_KEY)

    def extend_history(self, history_session: HistorySession) -> HistorySession:
        self.logger.info(f"Requesting response for session: {history_session.session_id}")
        resp = self.client.responses.create(
            model="gpt-4.1-mini",
            input=history_session.dump_for_openai(),
        )
        history_session.add_assistant_message(resp.output_text)
        return history_session
