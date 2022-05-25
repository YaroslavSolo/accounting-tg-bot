from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from bot.handlers.other_handlers import MenuKeyboardStates

from .material_add_handlers import register_handlers as register_material_add_handlers, add_material
from .material_view_handlers import register_handlers as register_material_view_handlers, view_material
from .material_edit_handlers import register_handlers as register_material_edit_handlers, edit_material


async def material_menu_kb_handler(message: types.Message, state: FSMContext):
    text = message.text
    if text == 'Добавить':
        await add_material(message, state)
    elif text == 'Посмотреть':
        await view_material(message, state)
    elif text == 'Изменить':
        await edit_material(message, state)


def register_handlers(dispatcher: Dispatcher):
    register_material_add_handlers(dispatcher)
    register_material_view_handlers(dispatcher)
    register_material_edit_handlers(dispatcher)
    dispatcher.register_message_handler(
        material_menu_kb_handler,
        content_types=['text'],
        state=MenuKeyboardStates.material
    )
