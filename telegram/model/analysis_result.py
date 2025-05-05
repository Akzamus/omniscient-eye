from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel

NUM_TO_NAME = {
    1: 'no_join',
    2: 'risk_join',
    3: 'maybe_join',
    4: 'join',
    5: 'must_join'
}


class ViewType(Enum):
    USERS_BRANCH = 'users_branch'
    CHATS_BRANCH = 'chats_branch'


class ChatsAnalysisResult(BaseModel):
    titles: list[str]
    total_participant_count: int
    active_participant_count: int
    participant_type_counts: dict[str, int]
    recommendation_counts: dict[str, int]
    participant_types: Optional[list[str]]

    def to_text(self, view_type: ViewType) -> str:
        head = f"📍 {' | '.join(self.titles)}"
        users_type = 'Chosen' if view_type == ViewType.USERS_BRANCH else 'Active'

        if view_type == ViewType.USERS_BRANCH and self.participant_types:
            head = f"🔍{' | '.join(self.participant_types)} in {head}"

        lines = [
            f'<b>{head}</b>',
            f'👥 Total users: ~ {self.total_participant_count}',
            f'🗣️ {users_type} users: {self.active_participant_count}',
            f'📊 <b>Types:</b>',
            *[f"  - {participant_type}: {count}" for participant_type, count in self.participant_type_counts.items()],
            f'📝 <b>Recommendations:</b>',
            *[f"  - {NUM_TO_NAME.get(int(recommendation), recommendation)}: {count}" for recommendation, count in self.recommendation_counts.items()],
        ]
        return '\n'.join(lines)


class ChatAnalysisResult(BaseModel):
    title: str
    participant_count: int
    active_participant_count: int
    participant_type_counts: dict[str, int]
    recommendation_counts: dict[str, int]

    def to_text(self, view_type: ViewType) -> str:
        users_type = 'Chosen' if view_type == ViewType.USERS_BRANCH else 'Active'
        lines = [
            f'📍 <b>{self.title}</b>',
            f'👥 Total users: ~ {self.participant_count}',
            f'🗣️ {users_type} users: {self.active_participant_count}',
            f'📊 <b>Types:</b>',
            *[f"  - {participant_type}: {count}" for participant_type, count in self.participant_type_counts.items()],
            f'📝 <b>Recommendations:</b>',
            *[f"  - {NUM_TO_NAME.get(int(recommendation), recommendation)}: {count}" for recommendation, count in self.recommendation_counts.items()],
        ]
        return '\n'.join(lines)


class UserGeneralAnalysisResult(BaseModel):
    chat_titles: list[str]
    participant_to_all_chats: tuple[int, int]
    average_impact: float
    average_recommendation: int
    participant_type_percentages: dict[str, float]
    explanation: dict[str, int]

    def to_text(self) -> str:
        chat_ratio = f'{self.participant_to_all_chats[0]}/{self.participant_to_all_chats[1]}'
        lines = [
            f"📍 <b>Chats: {chat_ratio}, {' | '.join(self.chat_titles)}</b>",
            f'👤 <b>Type:</b>',
            *[f"  - {participant_type} - {percent}%" for participant_type, percent in self.participant_type_percentages.items()],
            f'🔥 <b>Average impact:</b> {self.average_impact}',
            f'📝 <b>Average recommendation:</b> {NUM_TO_NAME.get(self.average_recommendation, self.average_recommendation)}',
            f'💬 <b>Explanation:</b>',
            *[f"  - {message_type}: {count}" for message_type, count in self.explanation.items() if count != 0],
        ]
        return '\n'.join(lines)


class UserAnalysisResult(BaseModel):
    chat_title: str
    participant_type: str
    impact: int
    recommendation: int
    explanation: dict[str, Any]

    def to_text(self) -> str:
        lines = [
            f'📍 <b>{self.chat_title}</b>',
            f'👤 <b>Type:</b> {self.participant_type}',
            f'🔥 <b>Impact:</b> {self.impact}',
            f'📝 <b>Recommendation:</b> {NUM_TO_NAME.get(self.recommendation, self.recommendation)}',
            f'💬 <b>Explanation:</b>',
            *[f"  - {message_type}: {count}" for message_type, count in self.explanation.items() if count != 0],
        ]
        return '\n'.join(lines)
