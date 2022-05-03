from aiogram import types, Dispatcher


async def echo(message: types.Message):
    print(message.from_user.id)
    await message.answer(message.text[len('/echo '):])


def register_handlers(dispatcher: Dispatcher):
    dispatcher.register_message_handler(echo, commands=['echo'])
