import logging
from io import BytesIO

from openpyxl.workbook import Workbook

import container

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from telegram.model.analysis_result import ViewType
from telegram.model.user_analysis_entity import TelegramUserAnalysisEntity
from telegram.utils import keyboard_builder
from telegram.utils.callback_helpers import handle_checkbox_interaction
from telegram.utils.text import Texts
from infra import excel_report_generator


router = Router()
logger = logging.getLogger(__file__)

SELECTED_CHAT_IDS = 'selected_chat_ids'
SELECTED_USER_TYPES = 'selected_user_types'


class UsersStates(StatesGroup):
    selecting_chats = State()
    selecting_user_types = State()
    showing_chats_info = State()
    showing_chats_info_detailed = State()


@router.message(lambda m: m.text == Texts.Bot.Button.Main.USERS)
async def show_chat_options(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=Texts.Bot.Message.SELECTING_USER_TYPES,
        reply_markup=keyboard_builder.build_checkbox_keyboard(
            options=keyboard_builder.get_user_type_options()
        )
    )
    await state.set_state(UsersStates.selecting_user_types)


@router.callback_query(UsersStates.selecting_user_types)
async def toggle_user_type_selection(callback: types.CallbackQuery, state: FSMContext):
    async def on_done(cb: types.CallbackQuery, st: FSMContext):
        await cb.message.edit_text(
            text=Texts.Bot.Message.SELECTING_CHATS,
            reply_markup=keyboard_builder.build_checkbox_keyboard(
                options=keyboard_builder.get_chat_options()
            )
        )
        await st.set_state(UsersStates.selecting_chats)

    await handle_checkbox_interaction(
        callback=callback,
        state=state,
        key=SELECTED_USER_TYPES,
        get_options=keyboard_builder.get_user_type_options,
        empty_warning=Texts.Bot.Message.USER_TYPE_SELECTION_EMPTY_WARNING,
        done_handler=on_done
    )


@router.callback_query(UsersStates.selecting_chats)
async def toggle_chat_selection(callback: types.CallbackQuery, state: FSMContext):
    async def on_done(cb: types.CallbackQuery, st: FSMContext):
        selected_chat_ids = await st.get_value(SELECTED_CHAT_IDS, [])
        participant_types = await st.get_value(SELECTED_USER_TYPES, [])
        chat_ids = list(map(int, selected_chat_ids))

        await cb.message.edit_text(
            text=container.telegram_chat_analyzer.analyze_chats(
                chat_ids=chat_ids,
                participant_types=participant_types
            ).to_text(ViewType.USERS_BRANCH),
            reply_markup=keyboard_builder.build_details_button()
        )
        await st.set_state(UsersStates.showing_chats_info)

    await handle_checkbox_interaction(
        callback=callback,
        state=state,
        key=SELECTED_CHAT_IDS,
        get_options=keyboard_builder.get_chat_options,
        empty_warning=Texts.Bot.Message.CHAT_SELECTION_EMPTY_WARNING,
        done_handler=on_done
    )


@router.callback_query(UsersStates.showing_chats_info)
async def handle_details(callback: types.CallbackQuery, state: FSMContext):
    user_input = callback.data
    selected_chat_ids = await state.get_value(SELECTED_CHAT_IDS, [])
    participant_types = await state.get_value(SELECTED_USER_TYPES, [])

    if user_input == 'details':
        chat_ids = list(map(int, selected_chat_ids))
        results = container.telegram_chat_analyzer.analyze_chats_detailed(
            chat_ids=chat_ids,
            participant_types=participant_types
        )
        formatted_text = f'\n{Texts.Bot.Message.SEPARATOR}\n\n'.join(
            r.to_text(ViewType.USERS_BRANCH) for r in results
        )

        workbook = Workbook()
        workbook.remove(workbook.active)

        chat_title_to_user_analysis = container.telegram_chat_analyzer.get_user_analysis_group_by_chat_title(
            chat_ids=chat_ids,
            participant_types=participant_types
        )

        for chat_title, user_analysis in chat_title_to_user_analysis.items():
            worksheet = workbook.create_sheet(chat_title)
            content: list[list[str]] = [TelegramUserAnalysisEntity.get_excel_headers()]

            for user_analys in user_analysis:
                content.append(user_analys.to_excel_row())

            excel_report_generator.fill_excel_sheet(worksheet, content)

        file_stream = BytesIO()
        workbook.save(file_stream)
        file_stream.seek(0)

        await callback.message.edit_text(formatted_text)
        await callback.message.answer_document(
            document=types.BufferedInputFile(
                file=file_stream.read(),
                filename=excel_report_generator.generate_unique_filename('report')
            )
        )
        await state.set_state(UsersStates.showing_chats_info_detailed)
        await state.clear()
