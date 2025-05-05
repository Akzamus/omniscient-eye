import asyncio

from telegram.bot import TelegramBot
import config
import infra.logger
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

bot = TelegramBot(
    token=config.TELEGRAM_BOT_TOKEN,
    dispatcher=Dispatcher(
        storage=MemoryStorage()
    )
)

asyncio.run(bot.run())