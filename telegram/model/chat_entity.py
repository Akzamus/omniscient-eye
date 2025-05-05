from pydantic import BaseModel, Field
from typing import Optional


class ChatEntity(BaseModel):
    telegram_id: int
    title: str
    participant_count: Optional[int]
    description: Optional[str] = Field(default=None)
    is_hidden: bool = Field(default=False)
