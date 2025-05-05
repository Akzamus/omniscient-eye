from operator import attrgetter

from cachetools import TTLCache, cachedmethod
from pymongo.synchronous.collection import Collection

from telegram.model.chat_entity import ChatEntity


class TelegramChatRepository:
    def __init__(self, collection: Collection, cache: TTLCache):
        self._collection = collection
        self._cache = cache

    @cachedmethod(attrgetter('_cache'), key=lambda *_: 'chats')
    def find_all(self) -> list[ChatEntity]:
        chats = self._collection.find({'is_hidden': False})
        return [ChatEntity(**doc) for doc in chats]

    def find_by_ids(self, ids: list[int]) -> list[ChatEntity]:
        chats = self._collection.find({'telegram_id': {'$in': ids}})
        return [ChatEntity(**doc) for doc in chats]

    def find_by_id(self, id: int) -> ChatEntity | None:
        doc = self._collection.find_one({'telegram_id': id})
        return ChatEntity(**doc) if doc else None

    def upsert(self, chat: ChatEntity) -> None:
        existing = self._collection.find_one({"telegram_id": chat.telegram_id})

        if existing:
            if "description" in existing:
                chat.description = existing["description"]
            if "is_hidden" in existing:
                chat.is_hidden = existing["is_hidden"]

        self._collection.update_one(
            {"telegram_id": chat.telegram_id},
            {"$set": chat.dict()},
            upsert=True
        )

    def get_id_to_chat_dict(self, chat_ids: list[int] | None = None) -> dict[int, ChatEntity]:
        chats = self.find_by_ids(chat_ids) if chat_ids else self.find_all()
        return {
            chat.telegram_id: chat
            for chat in chats
        }
