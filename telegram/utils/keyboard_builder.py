from typing import List, Union

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import container


def build_reply_keyboard(
        buttons: Union[List[str], List[List[str]]],
        one_time: bool = False,
        placeholder: str = "Choose option..."
) -> ReplyKeyboardMarkup:
    if buttons and isinstance(buttons[0], str):
        keyboard = [[KeyboardButton(text=btn) for btn in buttons]]
    else:
        keyboard = [[KeyboardButton(text=btn) for btn in row] for row in buttons]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        one_time_keyboard=one_time,
        input_field_placeholder=placeholder,
        resize_keyboard=True
    )


def build_checkbox_keyboard(
        options: dict[str, str],
        selected_keys: list[str] = None,
        final_button_text: str = 'Done',
        final_callback_data: str = 'done',
        columns: int = 1,
        show_check: bool = True
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    selected_keys = selected_keys or []

    for callback_data, label in options.items():
        check = "✅ " if show_check and callback_data in selected_keys else "☑️ " if show_check else ""
        builder.button(
            text=f"{check}{label}",
            callback_data=callback_data
        )

    if final_button_text:
        builder.button(text=final_button_text, callback_data=final_callback_data)

    builder.adjust(columns)
    return builder.as_markup()


def build_details_button() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Details',
        callback_data='details'
    )
    builder.adjust(1)
    return builder.as_markup()


def get_chat_options() -> dict[str, str]:
    return {
        str(chat.telegram_id): chat.title
        for chat in container.chat_repository.find_all()
    }


def get_user_type_options() -> dict[str, str]:
    return {
        user_type: user_type
        for user_type in container.telegram_chat_analyzer.get_distinct_user_types()
    }
