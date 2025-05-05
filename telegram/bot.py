from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import telegram.utils.keyboard_builder as keyboard_builder
from telegram.route import users_router, chats_router, per_user_router, home_router
from telegram.utils.text import Texts


class TelegramBot:
    def __init__(self, token: str, dispatcher: Dispatcher):
        self.bot = Bot(
            token=token,
            default=DefaultBotProperties(
                parse_mode=ParseMode.HTML
            )
        )
        self.dispatcher = dispatcher
        dispatcher.include_router(chats_router.router)
        dispatcher.include_router(users_router.router)
        dispatcher.include_router(per_user_router.router)
        dispatcher.include_router(home_router.router)
        self.setup_handlers()

    def setup_handlers(self):
        @self.dispatcher.message(Command("start"))
        async def start_handler(message: types.Message, state: FSMContext):
            await message.answer(
                text=Texts.Bot.Message.START,
                reply_markup=keyboard_builder.build_reply_keyboard(
                    buttons=[
                        [Texts.Bot.Button.Main.CHATS, Texts.Bot.Button.Main.USERS],
                        [Texts.Bot.Button.Main.PER_USER, Texts.Bot.Button.Main.HOME]
                    ]
                )
            )

    async def run(self):
        await self.dispatcher.start_polling(self.bot)
