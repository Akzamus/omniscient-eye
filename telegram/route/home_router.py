from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from telegram.utils.text import Texts

router = Router()


@router.message(lambda m: m.text == Texts.Bot.Button.Main.HOME)
async def show_writing_username_message(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(Texts.Bot.Message.HOME_PAGE)