from asgiref.sync import sync_to_async

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher.filters.state import State, StatesGroup

from products.service import *
from bot.bot_init import bot
from bot.validators.product_validators import *
from bot.validators.common import *
from bot.keyboards.common import main_kb, empty_inline_button, build_product_edit_kb, build_product_selection_kb
from bot.handlers.other_handlers import MenuKeyboardStates


class EditState(StatesGroup):
    start = State()


offset = 0
cb = CallbackData('stub', 'name', 'action')


async def edit_product(message: types.Message, state: FSMContext):
    global offset
    offset = 0

    product_names = await get_product_names(message.chat.id, offset)
    if not product_names:
        await message.answer('Нет сохраненных товаров', reply_markup=main_kb)
        await state.finish()
        return

    names_kb = build_product_selection_kb(product_names)

    await state.finish()
    await message.answer('Выберите товар для изменения', parse_mode='markdown', reply_markup=names_kb)


async def edit_product_next(callback: types.CallbackQuery):
    global offset
    product_count = await get_products_count(callback.message.chat.id)
    if offset + PRODUCT_NAMES_LIMIT > product_count - 1:
        await callback.answer('Просмотрены все товары')
        return

    offset += PRODUCT_NAMES_LIMIT
    names_kb = build_product_selection_kb(await get_product_names(callback.message.chat.id, offset))

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

    names_kb = build_product_selection_kb(await get_product_names(callback.message.chat.id, offset))

    await callback.message.edit_reply_markup(names_kb)
    await callback.answer()


# ---------------------------------------------- EDIT PRODUCT HANDLERS ---------------------------------------------- #
async def edit_selected_product_menu(callback):
    product_name = callback.data.split(':')[1]
    await callback.message.answer(
        f'*{product_name}*',
        parse_mode='markdown',
        reply_markup=build_product_edit_kb(product_name)
    )
    await callback.answer()


async def delete_selected_product(callback):
    delete_product(callback.message.chat.id, callback)
    await callback.message.answer('Товар удален', reply_markup=main_kb)
    await callback.answer('Товар удален')


async def edit_selected_product_option(callback: types.CallbackQuery, state: FSMContext):
    product_name = callback.data.split(':')[1]
    option = callback.data.split(':')[2]
    async with state.proxy() as data:
        data['name'] = product_name
        data['option'] = option

    message = ''
    if option == 'name':
        message = 'Введите новое имя'
    elif option == 'description':
        message = 'Введите новое описание'
    elif option == 'price':
        message = 'Введите новую цену'
    elif option == 'production_time':
        message = 'Введите новое время изготовления'
    elif option == 'amount':
        message = 'Введите измененное количество'

    await EditState.start.set()
    await bot.send_message(callback.message.chat.id, message)
    await callback.answer('')


async def edit_selected_product_option_save(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        product_name = data['name']
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
    await state.finish()
    await message.answer('Изменения сохранены', reply_markup=main_kb)


def register_handlers(dispatcher: Dispatcher):
    dispatcher.register_message_handler(edit_product, commands=['Изменить'], state=MenuKeyboardStates.product)
    dispatcher.register_callback_query_handler(edit_product_next, cb.filter(action=['next']))
    dispatcher.register_callback_query_handler(edit_product_prev, cb.filter(action=['prev']))
    dispatcher.register_callback_query_handler(edit_selected_product_menu, cb.filter(action=['edit']))
    dispatcher.register_callback_query_handler(
        edit_selected_product_option,
        cb.filter(action=['name', 'description', 'price', 'production_time']),
        state='*'
    )
    dispatcher.register_message_handler(edit_selected_product_option_save, state=EditState.start)