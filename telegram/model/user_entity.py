from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TelegramUserEntity(BaseModel):
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    language_code: Optional[str]
    is_admin: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @staticmethod
    def get_excel_headers() -> list[str]:
        return ['Id', 'Username', 'First name', 'Last name', 'Language', 'Created']

    def to_excel_row(self) -> list[str]:
        return [
            str(self.telegram_id),
            self.username or '',
            self.first_name or '',
            self.last_name or '',
            self.language_code or '',
            self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ]
