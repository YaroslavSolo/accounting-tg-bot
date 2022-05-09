from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from bot.handlers.other_handlers import MenuKeyboardStates

from .product_add_handlers import register_handlers as register_product_add_handlers, add_product
from .product_view_handlers import register_handlers as register_product_view_handlers, view_product
from .product_edit_handlers import register_handlers as register_product_edit_handlers, edit_product


async def product_menu_kb_handler(message: types.Message, state: FSMContext):
    text = message.text
    if text == 'Добавить':
        await add_product(message, state)
    elif text == 'Посмотреть':
        await view_product(message, state)
    elif text == 'Изменить':
        await edit_product(message, state)


def register_handlers(dispatcher: Dispatcher):
    register_product_add_handlers(dispatcher)
    register_product_view_handlers(dispatcher)
    register_product_edit_handlers(dispatcher)
    dispatcher.register_message_handler(
        product_menu_kb_handler,
        content_types=['text'],
        state=MenuKeyboardStates.product
    )
