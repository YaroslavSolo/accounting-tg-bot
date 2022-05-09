import datetime

from .common import raise_if_error


async def validate_description(message):
    text = message.text
    error_msg = ''
    if text == '':
        error_msg = 'Описание заказа не должно быть пустым'
    elif len(text) > 250:
        error_msg = 'Описание заказа слишком длинное'

    await raise_if_error(error_msg, message)


async def validate_deadline_date(message):
    text = message.text
    error_msg = ''
    try:
        datetime.datetime.strptime(text, '%d.%m.%Y')
    except Exception:
        error_msg = 'Введенная дата не соответствует формату'

    await raise_if_error(error_msg, message)


async def validate_deadline_time(message):
    text = message.text
    error_msg = ''
    try:
        datetime.datetime.strptime(text, '%H:%M')
    except Exception:
        error_msg = 'Введенное время не соответствует формату'

    await raise_if_error(error_msg, message)
