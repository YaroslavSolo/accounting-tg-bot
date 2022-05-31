from asgiref.sync import sync_to_async

from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher.filters.state import State, StatesGroup

from products.service import *
from materials.service import *
from bot.bot_init import bot
from bot.validators.product_validators import *
from bot.validators.common_validators import *
from bot.keyboards import main_kb, empty_inline_button, build_product_edit_kb, build_item_selection_kb


class ProductEditStates(StatesGroup):
    select_product = State()
    select_operation = State()
    save_changes = State()
    select_material = State()
    material_amount = State()


offset = 0
cb = CallbackData('stub', 'id', 'action')


async def edit_product(message: types.Message, state: FSMContext):
    global offset
    offset = 0

    product_names = await get_product_names_and_ids(message.chat.id, offset)
    if not product_names:
        await message.answer('Нет сохраненных товаров', reply_markup=main_kb)
        await state.finish()
        return

    names_kb = build_item_selection_kb(product_names)

    await message.answer('Выберите товар для изменения', parse_mode='markdown', reply_markup=names_kb)
    await state.finish()
    await ProductEditStates.select_product.set()


async def edit_product_next(callback: types.CallbackQuery):
    global offset
    product_count = await get_products_count(callback.message.chat.id)
    if offset + PRODUCT_NAMES_LIMIT > product_count - 1:
        await callback.answer('Показан конец списка')
        return

    offset += PRODUCT_NAMES_LIMIT
    names_kb = build_item_selection_kb(await get_product_names_and_ids(callback.message.chat.id, offset))

    await callback.message.edit_reply_markup(names_kb)
    await callback.answer()


async def edit_product_prev(callback: types.CallbackQuery):
    global offset
    if offset == 0:
        await callback.answer('Показано начало списка')
        return

    offset -= PRODUCT_NAMES_LIMIT
    if offset < 0:
        offset = 0

    names_kb = build_item_selection_kb(await get_product_names_and_ids(callback.message.chat.id, offset))

    await callback.message.edit_reply_markup(names_kb)
    await callback.answer()


async def edit_selected_product_menu(callback: types.CallbackQuery):
    await callback.message.delete()
    product_name = callback.data.split(':')[1]
    await callback.message.answer(await get_product_str(callback.message.chat.id, product_name), parse_mode='markdown')
    await callback.message.answer(
        'Выберите параметр для изменения или действие',
        reply_markup=build_product_edit_kb(product_name)
    )
    await callback.answer()
    await ProductEditStates.next()


async def edit_selected_product_option(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    product_name = callback.data.split(':')[1]
    option = callback.data.split(':')[2]
    async with state.proxy() as data:
        data['id'] = product_name
        data['option'] = option

    message = ''
    if option == 'name':
        message = 'Введите новое название'
    elif option == 'description':
        message = 'Введите новое описание'
    elif option == 'price':
        message = 'Введите новую цену'
    elif option == 'production_time':
        message = 'Введите новое время изготовления'
    elif option == 'amount':
        message = 'Введите измененное количество'

    await bot.send_message(callback.message.chat.id, message)
    await callback.answer('')
    await ProductEditStates.next()


async def edit_selected_product_option_save(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        product_name = data['id']
        option = data['option']

    product = await get_product(message.chat.id, product_name)

    if option == 'name':
        await validate_name(message)
        product.name = message.text
    elif option == 'description':
        await validate_description(message)
        product.description = message.text
    elif option == 'price':
        await validate_positive_int(message)
        product.price = int(message.text)
    elif option == 'production_time':
        await validate_positive_int(message, 1000)
        product.production_time = int(message.text)
    elif option == 'amount':
        await validate_positive_int(message, 1000000)
        product.amount = int(message.text)

    await sync_to_async(product.save)()
    await message.answer('Изменения сохранены', reply_markup=main_kb)
    await state.finish()


# ----------------------------------------------------------------------------------------------------------------------
async def select_material(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    global offset
    offset = 0

    material_names = await get_material_names(callback.message.chat.id, offset)
    if not material_names:
        await callback.message.answer('Нет сохраненных материалов', reply_markup=main_kb)
        await state.finish()
        return

    names_kb = build_item_selection_kb(material_names)
    async with state.proxy() as data:
        data['product'] = await get_product(callback.message.chat.id, callback.data.split(':')[1])

    await callback.message.answer('Выберите материал для добавления', parse_mode='markdown', reply_markup=names_kb)
    await ProductEditStates.select_material.set()


async def select_material_next(callback: types.CallbackQuery):
    global offset
    product_count = await get_materials_count(callback.message.chat.id)
    if offset + MATERIAL_NAMES_LIMIT > product_count - 1:
        await callback.answer('Показан конец списка')
        return

    offset += MATERIAL_NAMES_LIMIT
    names_kb = build_item_selection_kb(await get_material_names(callback.message.chat.id, offset))

    await callback.message.edit_reply_markup(names_kb)
    await callback.answer()


async def select_material_prev(callback: types.CallbackQuery):
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


async def add_selected_material(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    material_name = callback.data.split(':')[1]
    async with state.proxy() as data:
        data['material_name'] = material_name

    await callback.message.answer(f'*{material_name}*\nВведите количество', parse_mode='markdown')
    await callback.answer()


async def add_selected_material_amount(message: types.Message, state: FSMContext):
    await validate_positive_int(message, 10000)
    async with state.proxy() as data:
        product = data['product']
        material = await get_material(message.chat.id, data['material_name'])

    await save_product_materials(product, material, int(message.text))
    global offset
    offset = 0
    names_kb = build_item_selection_kb(await get_material_names(message.chat.id, offset))
    names_kb.row(InlineKeyboardButton(text='Завершить', callback_data=cb.new(id='', action='finish')))
    await message.answer('Материал добавлен')
    await message.answer('Выберите материал для добавления', reply_markup=names_kb)


async def save_product(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    async with state.proxy() as data:
        product = data['product']

    await sync_to_async(product.refresh_from_db)()
    await state.finish()
    await callback.message.answer(
        f'Информация о товаре сохранена:\n\n{await sync_to_async(product.__str__)()}',
        parse_mode='markdown',
        reply_markup=main_kb
    )
    await callback.answer()


async def clear_selected_product_materials(callback: types.CallbackQuery, state: FSMContext):
    await clear_materials(callback.message.chat.id, callback.data.split(':')[1])
    await callback.message.answer('Список материалов очищен', reply_markup=main_kb)
    await callback.answer('Список материалов очищен')
    await state.finish()


async def delete_selected_product(callback: types.CallbackQuery, state: FSMContext):
    await delete_product(callback.message.chat.id, callback.data.split(':')[1])
    await callback.message.answer('Товар удален', reply_markup=main_kb)
    await callback.answer('Товар удален')
    await state.finish()


def register_handlers(dispatcher: Dispatcher):
    dispatcher.register_callback_query_handler(
        edit_product_next,
        cb.filter(action=['next']),
        state=ProductEditStates.select_product
    )
    dispatcher.register_callback_query_handler(
        edit_product_prev,
        cb.filter(action=['prev']),
        state=ProductEditStates.select_product
    )
    dispatcher.register_callback_query_handler(
        edit_selected_product_menu,
        cb.filter(action=['e']),
        state=ProductEditStates.select_product
    )
    dispatcher.register_callback_query_handler(
        edit_selected_product_option,
        cb.filter(action=['name', 'description', 'price', 'production_time', 'amount']),
        state=ProductEditStates.select_operation
    )
    dispatcher.register_callback_query_handler(
        select_material,
        cb.filter(action=['add_materials']),
        state=ProductEditStates.select_operation
    )
    dispatcher.register_callback_query_handler(
        select_material_next,
        cb.filter(action=['next']),
        state=ProductEditStates.select_material
    )
    dispatcher.register_callback_query_handler(
        select_material_prev,
        cb.filter(action=['prev']),
        state=ProductEditStates.select_material
    )
    dispatcher.register_callback_query_handler(
        add_selected_material,
        cb.filter(action=['e']),
        state=ProductEditStates.select_material
    )
    dispatcher.register_message_handler(
        add_selected_material_amount,
        state=ProductEditStates.select_material
    )
    dispatcher.register_callback_query_handler(
        save_product,
        cb.filter(action=['finish']),
        state=ProductEditStates.select_material
    )
    dispatcher.register_callback_query_handler(
        clear_selected_product_materials,
        cb.filter(action=['clear']),
        state=ProductEditStates.select_operation
    )
    dispatcher.register_callback_query_handler(
        delete_selected_product,
        cb.filter(action=['delete_product']),
        state=ProductEditStates.select_operation
    )
    dispatcher.register_message_handler(edit_selected_product_option_save, state=ProductEditStates.save_changes)
