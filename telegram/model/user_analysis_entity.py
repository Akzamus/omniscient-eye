from typing import Any, Optional

from pydantic import BaseModel
from telegram.utils import text


class TelegramUserAnalysisEntity(BaseModel):
    chat_id: int
    chat_title: str
    user_id: Optional[int]
    username: Optional[str]
    type: str
    impact: int
    overall_mood: str
    overall_characteristic: int
    explanation: dict[str, str | int]
    recommendation: int

    @staticmethod
    def from_document(document: dict[str, Any]) -> 'TelegramUserAnalysisEntity':
        return TelegramUserAnalysisEntity(
            chat_id=document['chat_id'],
            chat_title=document['chat_name'],
            user_id=document.get('user_id', None),
            username=document.get('user_name', None),
            type=document['type'],
            impact=document['impact'],
            overall_mood=document['overall_mood'],
            overall_characteristic=document['overall_characteristic'],
            explanation=document['explanation'],
            recommendation=document['recommendation']
        )

    @staticmethod
    def get_excel_headers() -> list[str]:
        return ['Username', 'Type', 'Recommendation']

    def to_excel_row(self) -> list[str]:
        return [
            self.username or str(self.user_id) or '--Unknown--',
            self.type,
            text.RECOMMENDATION_NUMBER_TO_NAME.get(self.recommendation, self.recommendation)
        ]