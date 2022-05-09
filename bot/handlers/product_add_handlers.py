from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from products.service import *
from bot.validators.product_validators import *
from bot.validators.common import *
from bot.keyboards.common import main_kb
from bot.handlers.other_handlers import MenuKeyboardStates


class AddProductStates(StatesGroup):
    name = State()
    description = State()
    price = State()
    production_time = State()


async def add_product(message: types.Message, state: FSMContext):
    await state.finish()
    await AddProductStates.name.set()
    await message.answer('Введите имя товара', reply_markup=ReplyKeyboardRemove())


async def add_product_name(message: types.Message, state: FSMContext):
    await validate_name(message)
    async with state.proxy() as product:
        product['name'] = message.text
    await AddProductStates.next()
    await message.answer('Введите описание')


async def add_product_description(message: types.Message, state: FSMContext):
    await validate_description(message)
    async with state.proxy() as product:
        product['description'] = message.text
    await AddProductStates.next()
    await message.answer('Введите цену')


async def add_product_price(message: types.Message, state: FSMContext):
    await validate_positive_int(message)
    async with state.proxy() as product:
        product['price'] = int(message.text)
    await AddProductStates.next()
    await message.answer('Введите время изготовления в днях')


async def add_product_production_time(message: types.Message, state: FSMContext):
    await validate_positive_int(message, 1000)
    async with state.proxy() as product:
        product['production_time'] = int(message.text)

    async with state.proxy() as raw_product:
        await save_product(raw_product, message.chat.id)

    await state.finish()
    await message.answer('Товар добавлен', reply_markup=main_kb)


def register_handlers(dispatcher: Dispatcher):
    dispatcher.register_message_handler(add_product, commands=['Добавить'], state=MenuKeyboardStates.product)
    dispatcher.register_message_handler(add_product_name, state=AddProductStates.name)
    dispatcher.register_message_handler(add_product_description, state=AddProductStates.description)
    dispatcher.register_message_handler(add_product_price, state=AddProductStates.price)
    dispatcher.register_message_handler(add_product_production_time, state=AddProductStates.production_time)
