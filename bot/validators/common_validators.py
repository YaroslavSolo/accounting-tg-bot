import datetime


async def raise_if_error(error, message, info='Пожалуйста, повторите ввод'):
    if error != '':
        await message.answer(f'{error}\n{info}')
        raise ValueError(error)


async def validate_positive_int(message, maximum=1000000000):
    text = message.text
    error_msg = ''
    try:
        amount = int(text)
    except Exception:
        error_msg = 'Введено некорректное значение'
        return error_msg

    if amount < 1:
        error_msg = 'Число должно быть положительным'
    elif amount > maximum:
        error_msg = 'Введено слишком большое значение'

    await raise_if_error(error_msg, message)


async def validate_date(message):
    text = message.text
    error_msg = ''
    try:
        datetime.datetime.strptime(text, '%d.%m.%Y')
    except Exception:
        error_msg = 'Введенная дата некорректна или не соответствует формату дд.мм.гггг'

    await raise_if_error(error_msg, message)
