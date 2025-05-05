import logging

import cachetools
from pymongo import MongoClient
from telethon import TelegramClient

import config
from telegram.repo.chat_repository import TelegramChatRepository
from telegram.repo.telegram_chat_analyzer import TelegramChatAnalyzer

log = logging.getLogger(__file__)

ttl_cache = cachetools.TTLCache(
    maxsize=100,
    ttl=300
)

mongo_client = MongoClient(
    host=config.MONGODB_URL
)

telegram_client = TelegramClient(
    session=config.TELEGRAM_USER_USERNAME,
    api_id=config.TELEGRAM_API_ID,
    api_hash=config.TELEGRAM_API_HASH,
)

chat_repository = TelegramChatRepository(
    collection=mongo_client['omniscient-eye']['telegram_chats'],
    cache=ttl_cache
)

telegram_chat_analyzer = TelegramChatAnalyzer(
    database=mongo_client['telegram_users_analysis'],
    cache=ttl_cache,
    chat_repository=chat_repository
)
