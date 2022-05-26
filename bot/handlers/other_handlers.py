from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from asgiref.sync import sync_to_async

from orders.service import *
from products.service import *
from materials.service import *
from tgusers.models import User
from bot.keyboards import main_kb, menu_kb


class MenuKeyboardStates(StatesGroup):
    product = State()
    product_edit = State()
    order = State()
    order_edit = State()
    material = State()
    material_edit = State()
    statistics_period_start = State()
    statistics_period_end = State()
    statistics_select_partition = State()


@sync_to_async
def save_or_create_user(user_id, username=None):
    user, flag = User.objects.get_or_create(telegram_id=user_id)
    if username != user.username and username is not None:
        user.username = username
    user.save()
    return user, flag


async def start(message: types.Message, state: FSMContext):
    await state.finish()
    _, is_new = await save_or_create_user(message.chat.id, message.from_user.username)
    greet_message = f'С возвращением, {message.from_user.first_name}!'
    if is_new:
        greet_message = f'Привет, {message.from_user.first_name}!\nЭто бот для учета, начнем работу!'
    await message.answer(greet_message, reply_markup=main_kb)


async def menu(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Открыто главное меню', reply_markup=main_kb)


async def product_menu(message: types.Message):
    await MenuKeyboardStates.product.set()
    await message.answer('Что вы хотите сделать?', reply_markup=menu_kb)


async def order_menu(message: types.Message):
    await MenuKeyboardStates.order.set()
    await message.answer('Что вы хотите сделать?', reply_markup=menu_kb)


async def material_menu(message: types.Message):
    await MenuKeyboardStates.material.set()
    await message.answer('Что вы хотите сделать?', reply_markup=menu_kb)


async def statistics_menu(message: types.Message):
    await MenuKeyboardStates.statistics_period_start.set()
    await message.answer('Введите дату начала периода для подсчета статистики в формате дд.мм.гггг:')


async def info(message: types.Message):
    await message.answer('Здесь будет инструкция по использованию бота')


async def clear_products_handler(message: types.Message):
    await clear_products(message.chat.id)
    await message.answer('Все товары были удалены')


async def clear_orders_handler(message: types.Message):
    await clear_orders(message.chat.id)
    await message.answer('Все заказы были удалены')


async def clear_materials_handler(message: types.Message):
    await clear_materials(message.chat.id)
    await message.answer('Все материалы были удалены')


async def main_kb_handler(message: types.Message):
    text = message.text
    if text == 'Товары':
        await product_menu(message)
    elif text == 'Заказы':
        await order_menu(message)
    elif text == 'Материалы':
        await material_menu(message)
    elif text == 'Статистика продаж':
        await statistics_menu(message)


def register_handlers(dispatcher: Dispatcher):
    dispatcher.register_message_handler(start, commands=['start', 's'], state='*')
    dispatcher.register_message_handler(menu, commands=['menu'], state='*')
    dispatcher.register_message_handler(product_menu, commands=['Товары'])
    dispatcher.register_message_handler(order_menu, commands=['Заказы'])
    dispatcher.register_message_handler(material_menu, commands=['Материалы'])
    dispatcher.register_message_handler(statistics_menu, commands=['Статистика продаж'])
    dispatcher.register_message_handler(info, commands=['info'])
    dispatcher.register_message_handler(clear_products_handler, commands=['clearproducts'])
    dispatcher.register_message_handler(clear_orders_handler, commands=['clearorders'])
    dispatcher.register_message_handler(clear_materials_handler, commands=['clearmaterials'])
    dispatcher.register_message_handler(main_kb_handler, content_types=['text'])
