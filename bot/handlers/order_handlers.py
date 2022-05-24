from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from bot.handlers.other_handlers import MenuKeyboardStates

from .order_add_handlers import register_handlers as register_order_add_handlers, add_order
from .order_view_handlers import register_handlers as register_order_view_handlers, view_order
from .order_edit_handlers import register_handlers as register_order_edit_handlers, edit_order


async def menu_kb_handler(message: types.Message, state: FSMContext):
    text = message.text
    if text == 'Добавить':
        await add_order(message, state)
    elif text == 'Посмотреть':
        await view_order(message, state)
    elif text == 'Изменить':
        await edit_order(message, state)


def register_handlers(dispatcher: Dispatcher):
    register_order_add_handlers(dispatcher)
    register_order_view_handlers(dispatcher)
    register_order_edit_handlers(dispatcher)
    dispatcher.register_message_handler(menu_kb_handler, content_types=['text'], state=MenuKeyboardStates.order)
