from typing import Callable, Awaitable
from aiogram import types
from aiogram.fsm.context import FSMContext
from telegram.utils import keyboard_builder


async def handle_checkbox_interaction(
    callback: types.CallbackQuery,
    state: FSMContext,
    *,
    key: str,
    get_options: Callable[[], dict[str, str]],
    empty_warning: str,
    done_handler: Callable[[types.CallbackQuery, FSMContext], Awaitable[None]],
):
    data = await state.get_data()
    selected_items = data.get(key, [])
    user_input = callback.data
    options = get_options()

    if user_input == "done":
        if not selected_items:
            await callback.answer(text=empty_warning, show_alert=True)
            return
        await done_handler(callback, state)
        return

    if user_input in options:
        if user_input in selected_items:
            selected_items.remove(user_input)
        else:
            selected_items.append(user_input)
        await state.update_data({key: selected_items})

    await callback.message.edit_reply_markup(
        reply_markup=keyboard_builder.build_checkbox_keyboard(
            options=options,
            selected_keys=selected_items
        )
    )
    await callback.answer()
