import logging
import asyncio
from typing import Optional

from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import Channel

import container
from telegram.model.chat_entity import ChatEntity

logger = logging.getLogger(__name__)


async def get_chat_info(chat_username: str) -> Optional[ChatEntity]:
    async with container.telegram_client as client:
        try:
            entity: Channel = await client.get_entity(chat_username)
            full_info = await client(GetFullChannelRequest(channel=entity))
            participants: Optional[int] = getattr(full_info.full_chat, 'participants_count', 0)

            return ChatEntity(
                telegram_id=entity.id,
                title=entity.title,
                participant_count=participants
            )
        except Exception as e:
            logging.warning(f"❌ Ошибка при получении {chat_username}: {e}")
            return None


async def main() -> None:
    chat_usernames = [
        "SantaDropChat",
        "lobsters_chat",
        "NYM_Russian",
        "satoshifriends",
        "nymchan_help_chat",
        "classicnarnia",
        "sophoncis",
        "Gagarin_talk",
        "nymchan"
    ]

    for username in chat_usernames:
        chat = await get_chat_info(username)
        if chat:
            container.chat_repository.upsert(chat)
            logging.info(f"✅ Обновлён чат: {chat.title} (id: {chat.telegram_id})")


if __name__ == '__main__':
    asyncio.run(main())
