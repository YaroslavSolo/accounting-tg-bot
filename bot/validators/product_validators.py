from .common import raise_if_error
from products.service import *


async def validate_name(message):
    text = message.text
    error_msg = ''
    if text == '':
        error_msg = 'Название товара не должно быть пустым'
    elif len(text) > 64:
        error_msg = 'Название товара слишком длинное'

    if await get_product(message.chat.id, text) is not None:
        error_msg = 'Товар с таким именем уже существует'

    await raise_if_error(error_msg, message)


async def validate_description(message):
    text = message.text
    error_msg = ''
    if len(text) > 250:
        error_msg = 'Описание товара слишком длинное'

    await raise_if_error(error_msg, message)
