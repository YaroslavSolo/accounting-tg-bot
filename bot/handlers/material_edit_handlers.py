from asgiref.sync import sync_to_async

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher.filters.state import State, StatesGroup

from materials.service import *
from bot.bot_init import bot
from bot.validators.material_validators import *
from bot.validators.common_validators import *
from bot.keyboards import main_kb, empty_inline_button, build_material_edit_kb, build_item_selection_kb


class MaterialEditStates(StatesGroup):
    select_material = State()
    select_operation = State()
    save_changes = State()


offset = 0
cb = CallbackData('stub', 'id', 'action')


async def edit_material(message: types.Message, state: FSMContext):
    global offset
    offset = 0

    material_names = await get_material_names(message.chat.id, offset)
    if not material_names:
        await message.answer('Нет сохраненных материалов', reply_markup=main_kb)
        await state.finish()
        return

    names_kb = build_item_selection_kb(material_names)

    await message.answer('Выберите материал для изменения', parse_mode='markdown', reply_markup=names_kb)
    await state.finish()
    await MaterialEditStates.select_material.set()


async def edit_material_next(callback: types.CallbackQuery):
    global offset
    product_count = await get_materials_count(callback.message.chat.id)
    if offset + MATERIAL_NAMES_LIMIT > product_count - 1:
        await callback.answer('Показан конец списка')
        return

    offset += MATERIAL_NAMES_LIMIT
    names_kb = build_item_selection_kb(await get_material_names(callback.message.chat.id, offset))

    await callback.message.edit_reply_markup(names_kb)
    await callback.answer()


async def edit_material_prev(callback: types.CallbackQuery):
    global offset
    if offset == 0:
        await callback.answer('Показано начало списка')
        return

    offset -= MATERIAL_NAMES_LIMIT
    if offset < 0:
        offset = 0

    names_kb = build_item_selection_kb(await get_material_names(callback.message.chat.id, offset))

    await callback.message.edit_reply_markup(names_kb)
    await callback.answer()


async def edit_selected_material_menu(callback: types.CallbackQuery):
    await callback.message.delete()
    material_name = callback.data.split(':')[1]
    await callback.message.answer(
        await get_material_str(callback.message.chat.id, material_name),
        parse_mode='markdown'
    )
    await callback.message.answer(
        'Выберите поле для изменения',
        parse_mode='markdown',
        reply_markup=build_material_edit_kb(material_name)
    )
    await callback.answer()
    await MaterialEditStates.next()


async def edit_selected_material_option(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    material_name = callback.data.split(':')[1]
    option = callback.data.split(':')[2]
    async with state.proxy() as data:
        data['id'] = material_name
        data['option'] = option

    message = ''
    if option == 'name':
        message = 'Введите новое название'
    elif option == 'price':
        message = 'Введите новую цену'
    elif option == 'amount':
        message = 'Введите измененное количество'

    await bot.send_message(callback.message.chat.id, message)
    await callback.answer('')
    await MaterialEditStates.next()


async def edit_selected_material_option_save(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        material_name = data['id']
        option = data['option']

    material = await get_material(message.chat.id, material_name)

    if option == 'name':
        await validate_name(message)
        material.name = message.text
    elif option == 'price':
        await validate_positive_int(message)
        material.price = int(message.text)
    elif option == 'amount':
        await validate_positive_int(message, 1000000)
        material.amount = int(message.text)

    await sync_to_async(material.save)()
    await message.answer('Изменения сохранены', reply_markup=main_kb)
    await state.finish()


async def delete_selected_material(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await delete_material(callback.message.chat.id, callback.data.split(':')[1])
    await callback.message.answer('Материал удален', reply_markup=main_kb)
    await callback.answer('Материал удален')
    await state.finish()


def register_handlers(dispatcher: Dispatcher):
    dispatcher.register_callback_query_handler(
        edit_material_next,
        cb.filter(action=['next']),
        state=MaterialEditStates.select_material
    )
    dispatcher.register_callback_query_handler(
        edit_material_prev,
        cb.filter(action=['prev']),
        state=MaterialEditStates.select_material
    )
    dispatcher.register_callback_query_handler(
        edit_selected_material_menu,
        cb.filter(action=['edit']),
        state=MaterialEditStates.select_material
    )
    dispatcher.register_callback_query_handler(
        edit_selected_material_option,
        cb.filter(action=['name', 'price', 'amount']),
        state=MaterialEditStates.select_operation
    )
    dispatcher.register_callback_query_handler(
        delete_selected_material,
        cb.filter(action=['delete_material']),
        state=MaterialEditStates.select_operation
    )
    dispatcher.register_message_handler(edit_selected_material_option_save, state=MaterialEditStates.save_changes)
