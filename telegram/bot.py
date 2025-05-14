from io import BytesIO

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from openpyxl.workbook import Workbook

import container
import telegram.utils.keyboard_builder as keyboard_builder
from infra import excel_report_generator
from telegram.model.user_entity import TelegramUserEntity
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
        @self.dispatcher.message(Command('start'))
        async def start_handler(message: types.Message, state: FSMContext):
            await state.clear()
            user = message.from_user

            if not container.user_repository.find_by_id(user.id):
                container.user_repository.save(
                    user=TelegramUserEntity(
                        telegram_id=user.id,
                        username=user.username,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        language_code=user.language_code
                    )
                )

            await message.answer(
                text=Texts.Bot.Message.START,
                reply_markup=keyboard_builder.build_reply_keyboard(
                    buttons=[
                        [Texts.Bot.Button.Main.CHATS, Texts.Bot.Button.Main.USERS],
                        [Texts.Bot.Button.Main.PER_USER, Texts.Bot.Button.Main.HOME]
                    ]
                )
            )

        @self.dispatcher.message(Command('users'))
        async def users_handler(message: types.Message, state: FSMContext):
            user = container.user_repository.find_by_id(message.from_user.id)
            if not user or not user.is_admin:
                await message.answer(Texts.Bot.Message.ACCESS_ERROR)
                return

            content: list[list[str]] = [TelegramUserEntity.get_excel_headers()]

            for telegram_user in container.user_repository.find_all():
                content.append(telegram_user.to_excel_row())

            workbook = Workbook()
            worksheet = workbook.active
            worksheet.title = 'Users'
            excel_report_generator.fill_excel_sheet(worksheet, content)

            file_stream = BytesIO()
            workbook.save(file_stream)
            file_stream.seek(0)

            await message.answer_document(
                document=types.BufferedInputFile(
                    file=file_stream.read(),
                    filename=excel_report_generator.generate_unique_filename('users')
                )
            )



    async def run(self):
        await self.dispatcher.start_polling(self.bot)
