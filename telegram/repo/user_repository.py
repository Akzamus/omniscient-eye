from pymongo.synchronous.collection import Collection

from telegram.model.user_entity import TelegramUserEntity


class TelegramUserRepository:
    def __init__(self, collection: Collection):
        self._collection = collection

    def find_by_id(self, id: int) -> TelegramUserEntity | None:
        doc = self._collection.find_one({'telegram_id': id})
        return TelegramUserEntity(**doc) if doc else None

    def find_all(self) -> list[TelegramUserEntity]:
        users = self._collection.find()
        return [TelegramUserEntity(**doc) for doc in users]

    def save(self, user: TelegramUserEntity):
        self._collection.insert_one(user.dict())
