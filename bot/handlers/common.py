from aiogram import types, Dispatcher
from bot.keyboards.common import main_keyboard


async def start(message: types.Message):
    await message.answer('Привет, это бот для учета, начнем работу!', reply_markup=main_keyboard)


def register_handlers(dispatcher: Dispatcher):
    dispatcher.register_message_handler(start, commands=['start', 'help'])
