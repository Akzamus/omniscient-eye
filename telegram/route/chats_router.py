import logging

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import container
from telegram.model.analysis_result import ViewType
from telegram.utils import keyboard_builder
from telegram.utils.callback_helpers import handle_checkbox_interaction
from telegram.utils.text import Texts

router = Router()
logger = logging.getLogger(__file__)

SELECTED_CHAT_IDS = 'selected_chat_ids'


class ChatsStates(StatesGroup):
    selecting_chats = State()
    showing_chats_info = State()
    showing_chats_info_detailed = State()


@router.message(lambda m: m.text == Texts.Bot.Button.Main.CHATS)
async def show_chat_options(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=Texts.Bot.Message.SELECTING_CHATS,
        reply_markup=keyboard_builder.build_checkbox_keyboard(
            options=keyboard_builder.get_chat_options()
        )
    )
    await state.set_state(ChatsStates.selecting_chats)


@router.callback_query(ChatsStates.selecting_chats)
async def toggle_chat_selection(callback: types.CallbackQuery, state: FSMContext):
    async def on_done(cb: types.CallbackQuery, st: FSMContext):
        selected_chat_ids = await st.get_value(SELECTED_CHAT_IDS, [])
        chat_ids = list(map(int, selected_chat_ids))
        await cb.message.edit_text(
            text=container.telegram_chat_analyzer.analyze_chats(chat_ids).to_text(ViewType.CHATS_BRANCH),
            reply_markup=keyboard_builder.build_details_button()
        )
        await st.set_state(ChatsStates.showing_chats_info)

    await handle_checkbox_interaction(
        callback=callback,
        state=state,
        key=SELECTED_CHAT_IDS,
        get_options=keyboard_builder.get_chat_options,
        empty_warning=Texts.Bot.Message.CHAT_SELECTION_EMPTY_WARNING,
        done_handler=on_done
    )


@router.callback_query(ChatsStates.showing_chats_info)
async def handle_details(callback: types.CallbackQuery, state: FSMContext):
    user_input = callback.data
    selected_chat_ids = await state.get_value(SELECTED_CHAT_IDS, [])

    if user_input == 'details':
        chat_ids = list(map(int, selected_chat_ids))
        results = container.telegram_chat_analyzer.analyze_chats_detailed(chat_ids)
        formatted_text = f'\n{Texts.Bot.Message.SEPARATOR}\n\n'.join(
            r.to_text(ViewType.CHATS_BRANCH) for r in results
        )
        await callback.message.edit_text(formatted_text)
        await state.set_state(ChatsStates.showing_chats_info_detailed)
        await state.clear()
