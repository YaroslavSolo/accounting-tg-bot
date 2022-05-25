from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from materials.service import *
from bot.validators.common_validators import *
from bot.validators.material_validators import *
from bot.keyboards.common import main_kb


class AddMaterialStates(StatesGroup):
    name = State()
    price = State()
    amount = State()


async def add_material(message: types.Message, state: FSMContext):
    await state.finish()
    await AddMaterialStates.name.set()
    await message.answer('Введите название материала', reply_markup=ReplyKeyboardRemove())


async def add_material_name(message: types.Message, state: FSMContext):
    await validate_name(message)
    async with state.proxy() as product:
        product['name'] = message.text
    await AddMaterialStates.next()
    await message.answer('Введите цену за единицу материала')


async def add_material_price(message: types.Message, state: FSMContext):
    await validate_positive_int(message)
    async with state.proxy() as product:
        product['price'] = int(message.text)
    await AddMaterialStates.next()
    await message.answer('Введите начальное количество материала - целое число')


async def add_material_amount(message: types.Message, state: FSMContext):
    await validate_positive_int(message, 1000000)
    async with state.proxy() as product:
        product['amount'] = int(message.text)
        await save_material(product, message.chat.id)
    await state.finish()
    await message.answer('Информация о материале добавлена', reply_markup=main_kb)


def register_handlers(dispatcher: Dispatcher):
    dispatcher.register_message_handler(add_material_name, state=AddMaterialStates.name)
    dispatcher.register_message_handler(add_material_price, state=AddMaterialStates.price)
    dispatcher.register_message_handler(add_material_amount, state=AddMaterialStates.amount)
