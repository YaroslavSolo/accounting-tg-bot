from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


start_button = KeyboardButton('Начать работу')
start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)  # чтобы кнопки подстраивались под размер содержимого
start_keyboard.add(start_button)

view_button = KeyboardButton('Посмотреть')
add_button = KeyboardButton('Добавить')
update_button = KeyboardButton('Редактировать')
statistics_button = KeyboardButton('Статистика продаж')
main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.row(view_button, add_button, update_button)
main_keyboard.row(statistics_button)

#  .row(b1, b2, b3) - кнопки в строку
#  .insert(b1) - если есть место в текущей строке, поместить туда кнопку
