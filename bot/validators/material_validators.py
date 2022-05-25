from .common_validators import raise_if_error
from materials.service import *


async def validate_name(message):
    text = message.text
    error_msg = ''
    if text == '':
        error_msg = 'Название материала не должно быть пустым'
    elif len(text) > 64:
        error_msg = 'Название материала слишком длинное'

    if await get_material(message.chat.id, text) is not None:
        error_msg = 'Материал с таким названием уже существует'

    await raise_if_error(error_msg, message)
