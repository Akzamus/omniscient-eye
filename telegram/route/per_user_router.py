import logging

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import container
from telegram.utils import keyboard_builder
from telegram.utils.text import Texts

router = Router()
logger = logging.getLogger(__file__)

USER_ID = 'user_id'


class PerUserStates(StatesGroup):
    writing_username = State()
    showing_user_info = State()
    showing_user_info_detailed = State()


@router.message(lambda m: m.text == Texts.Bot.Button.Main.PER_USER)
async def show_writing_username_message(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(Texts.Bot.Message.WRITING_USER_USERNAME)
    await state.set_state(PerUserStates.writing_username)


@router.message(PerUserStates.writing_username)
async def handle_username(message: types.Message, state: FSMContext):
    username = message.text
    user_entity = None

    async with container.telegram_client as client:
        try:
            user_entity = await client.get_entity(username)
        except (ValueError, TypeError):
            await message.answer(Texts.Bot.Message.INCORRECT_USERNAME_WARNING)
            return

        user_id = user_entity.id

        if not container.telegram_chat_analyzer.has_analysis_for_user(user_id):
            await message.answer(Texts.Bot.Message.USER_DATA_NOT_FOUND.format(user_id))
            return

        await state.update_data(user_id=user_id)
        await message.answer(
            text=container.telegram_chat_analyzer.analyze_user(user_id).to_text(),
            reply_markup=keyboard_builder.build_details_button()
        )
        await state.set_state(PerUserStates.showing_user_info)


@router.callback_query(PerUserStates.showing_user_info)
async def handle_details(callback: types.CallbackQuery, state: FSMContext):
    user_input = callback.data
    user_id = await state.get_value(USER_ID, 0)

    if user_input == 'details':
        results = container.telegram_chat_analyzer.analyze_user_detailed(user_id)
        formatted_text = f'\n{Texts.Bot.Message.SEPARATOR}\n\n'.join(
            r.to_text() for r in results
        )
        await callback.message.edit_text(formatted_text)
        await state.set_state(PerUserStates.showing_user_info_detailed)
        await state.clear()

