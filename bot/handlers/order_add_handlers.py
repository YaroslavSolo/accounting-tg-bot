import datetime
from asgiref.sync import sync_to_async

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardButton


from orders.service import *
from products.service import *
from bot.validators.order_validators import *
from bot.validators.common_validators import *
from bot.keyboards.common import main_kb, build_item_selection_kb


offset = 0
cb = CallbackData('stub', 'name', 'action')


class AddOrderStates(StatesGroup):
    description = State()
    deadline_date = State()
    deadline_time = State()
    product = State()
    finish = State()


async def add_order(message: types.Message, state: FSMContext):
    await state.finish()
    await AddOrderStates.description.set()
    await message.answer('Введите описание заказа', reply_markup=ReplyKeyboardRemove())


async def add_order_description(message: types.Message, state: FSMContext):
    await validate_description(message)
    async with state.proxy() as order:
        order['description'] = message.text
    await AddOrderStates.next()
    await message.answer('Введите дату завершения заказа (дедлайн) в формате дд.мм.гггг')


async def add_order_deadline_date(message: types.Message, state: FSMContext):
    await validate_date(message)
    async with state.proxy() as order:
        deadline = datetime.datetime.strptime(message.text, '%d.%m.%Y')
        order['deadline_date'] = deadline
    await AddOrderStates.next()
    await message.answer('Введите время завершения заказа в формате чч:мм')


async def add_order_deadline_time(message: types.Message, state: FSMContext):
    await validate_deadline_time(message)
    async with state.proxy() as order:
        deadline = datetime.datetime.strptime(message.text, '%H:%M')
        order['deadline_time'] = deadline

    async with state.proxy() as order:
        order['saved_order'] = await save_order(order, message.chat.id)

    global offset
    offset = 0
    await AddOrderStates.next()
    products_list_kb = build_item_selection_kb(await get_product_names(message.chat.id, offset))
    products_list_kb.row(InlineKeyboardButton(text='Завершить', callback_data=cb.new(name='', action='finish')))
    await message.answer('Выберите товары в заказ', reply_markup=products_list_kb)


async def product_list_next(callback: types.CallbackQuery):
    global offset
    product_count = await get_products_count(callback.message.chat.id)
    if offset + PRODUCT_NAMES_LIMIT > product_count - 1:
        await callback.answer('Показан конец списка')
        return

    offset += PRODUCT_NAMES_LIMIT
    names_kb = build_item_selection_kb(await get_product_names(callback.message.chat.id, offset))
    names_kb.row(InlineKeyboardButton(text='Завершить', callback_data=cb.new(name='', action='finish')))

    await callback.message.edit_reply_markup(names_kb)
    await callback.answer()


async def product_list_prev(callback: types.CallbackQuery):
    global offset
    if offset == 0:
        await callback.answer('Показано начало списка')
        return

    offset -= PRODUCT_NAMES_LIMIT
    if offset < 0:
        offset = 0

    names_kb = build_item_selection_kb(await get_product_names(callback.message.chat.id, offset))
    names_kb.row(InlineKeyboardButton(text='Завершить', callback_data=cb.new(name='', action='finish')))

    await callback.message.edit_reply_markup(names_kb)
    await callback.answer()


async def add_order_products_list(callback: types.CallbackQuery, state: FSMContext):
    product_name = callback.data.split(':')[1]
    async with state.proxy() as data:
        data['product_name'] = product_name

    await callback.message.delete()
    await callback.message.answer(f'*{product_name}*\nВведите количество', parse_mode='markdown')
    await callback.answer()


async def add_order_product_amount(message: types.Message, state: FSMContext):
    await validate_positive_int(message, 10000)
    async with state.proxy() as data:
        product = await get_product(message.chat.id, data['product_name'])
        order = data['saved_order']

    await save_order_products(order, product, int(message.text))
    global offset
    offset = 0
    names_kb = build_item_selection_kb(await get_product_names(message.chat.id, offset))
    names_kb.row(InlineKeyboardButton(text='Завершить', callback_data=cb.new(name='', action='finish')))
    await message.answer('Товар добавлен в заказ')
    await message.answer('Выберите товары в заказ', reply_markup=names_kb)


async def add_order_finish(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    async with state.proxy() as data:
        order = data['saved_order']

    await sync_to_async(order.refresh_from_db)()
    await state.finish()
    await callback.message.answer(
        f'Сохранен заказ:\n\n{await sync_to_async(order.__str__)()}',
        parse_mode='markdown',
        reply_markup=main_kb
    )
    await callback.answer()


def register_handlers(dispatcher: Dispatcher):
    dispatcher.register_message_handler(add_order_description, state=AddOrderStates.description)
    dispatcher.register_message_handler(add_order_deadline_date, state=AddOrderStates.deadline_date)
    dispatcher.register_message_handler(add_order_deadline_time, state=AddOrderStates.deadline_time)
    dispatcher.register_message_handler(add_order_product_amount, state=AddOrderStates.product)
    dispatcher.register_callback_query_handler(
        add_order_finish,
        cb.filter(action=['finish']),
        state=AddOrderStates.product
    )
    dispatcher.register_callback_query_handler(
        add_order_products_list,
        cb.filter(action=['edit']),
        state=AddOrderStates.product
    )
    dispatcher.register_callback_query_handler(
        product_list_next,
        cb.filter(action=['next']),
        state=AddOrderStates.product
    )
    dispatcher.register_callback_query_handler(
        product_list_prev,
        cb.filter(action=['prev']),
        state=AddOrderStates.product
    )
