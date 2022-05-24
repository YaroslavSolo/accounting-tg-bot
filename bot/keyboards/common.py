from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData


start_button = KeyboardButton('/Начать работу')
start_kb = ReplyKeyboardMarkup(resize_keyboard=True)
start_kb.add(start_button)


view_button = KeyboardButton(text='Посмотреть')
add_button = KeyboardButton('Добавить')
edit_button = KeyboardButton('Изменить')
menu_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
menu_kb.row(view_button, add_button, edit_button)


product_button = KeyboardButton('Товары')
order_button = KeyboardButton('Заказы')
statistics_button = KeyboardButton('Статистика продаж')
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.row(product_button, order_button)
main_kb.row(statistics_button)


empty_inline_button = InlineKeyboardButton(text='  ', callback_data='none')


day_button = InlineKeyboardButton(text='День', callback_data='D')
week_button = InlineKeyboardButton(text='Неделя', callback_data='W-MON')
month_button = InlineKeyboardButton(text='Месяц', callback_data='M')
partition_type_kb = InlineKeyboardMarkup(row_width=5, resize_keyboard=True)
partition_type_kb.row(day_button, week_button, month_button)


def build_pagination_kb(callback_data):
    previous_button = InlineKeyboardButton(text='⬅️', callback_data='prev' + '_' + callback_data)
    empty_button = InlineKeyboardButton(text='  ', callback_data='none' + '_' + callback_data)
    next_button = InlineKeyboardButton(text='➡️', callback_data='next' + '_' + callback_data)
    pagination_kb = InlineKeyboardMarkup(row_width=5, resize_keyboard=True)
    pagination_kb.row(previous_button, empty_button, next_button)
    return pagination_kb


def build_product_selection_kb(product_names):
    cb = CallbackData('stub', 'name', 'action')

    product_name_buttons = map(
        lambda name: InlineKeyboardButton(text=name, callback_data=cb.new(name=name, action='edit')),
        product_names
    )
    previous_button = InlineKeyboardButton(text='⬅️', callback_data=cb.new(name='', action='prev'))
    next_button = InlineKeyboardButton(text='➡️', callback_data=cb.new(name='', action='next'))

    names_kb = InlineKeyboardMarkup(row_width=1)
    names_kb.add(*product_name_buttons)
    names_kb.row(previous_button, empty_inline_button, next_button)

    return names_kb


def build_product_edit_kb(product_name):
    cb = CallbackData('stub', 'id', 'action')

    name_button = InlineKeyboardButton(
        text='Название',
        callback_data=cb.new(id=product_name, action='name')
    )
    description_button = InlineKeyboardButton(
        text='Описание',
        callback_data=cb.new(id=product_name, action='description')
    )
    price_button = InlineKeyboardButton(
        text='Цена',
        callback_data=cb.new(id=product_name, action='price')
    )
    production_time_button = InlineKeyboardButton(
        text='Время изготовления',
        callback_data=cb.new(id=product_name, action='production_time')
    )
    amount_button = InlineKeyboardButton(
        text='Количество',
        callback_data=cb.new(id=product_name, action='amount')
    )
    delete_button = InlineKeyboardButton(
        text='Удалить ❌',
        callback_data=cb.new(id=product_name, action='delete_product')
    )

    edit_kb = InlineKeyboardMarkup(row_width=1).add(
        name_button,
        description_button,
        price_button,
        production_time_button,
        amount_button,
        delete_button
    )

    return edit_kb


def build_order_edit_kb(order_id):
    cb = CallbackData('stub', 'id', 'action')

    description_button = InlineKeyboardButton(
        text='Описание',
        callback_data=cb.new(id=order_id, action='description')
    )
    deadline_date_button = InlineKeyboardButton(
        text='Дата дедлайна',
        callback_data=cb.new(id=order_id, action='deadline_date')
    )
    deadline_time_button = InlineKeyboardButton(
        text='Время дедлайна',
        callback_data=cb.new(id=order_id, action='deadline_time')
    )
    delete_button = InlineKeyboardButton(
        text='Удалить ❌',
        callback_data=cb.new(id=order_id, action='delete_order')
    )

    edit_kb = InlineKeyboardMarkup(row_width=1).add(
        description_button,
        deadline_date_button,
        deadline_time_button,
        delete_button
    )

    return edit_kb
