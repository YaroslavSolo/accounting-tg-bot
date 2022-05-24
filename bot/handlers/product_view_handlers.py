from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from products.service import *
from bot.bot_init import bot, dispatcher
from bot.keyboards.common import main_kb, build_pagination_kb


offset = 0


async def view_product(message: types.Message, state: FSMContext):
    global offset
    offset = 0
    await state.finish()
    await message.answer(f'Всего товаров: {await get_products_count(message.chat.id)}', reply_markup=main_kb)
    await message.answer(
        await get_products_str(message.chat.id, offset),
        parse_mode='markdown',
        reply_markup=build_pagination_kb('product')
    )


async def view_product_next(callback: types.CallbackQuery):
    global offset
    product_count = await get_products_count(callback.message.chat.id)
    if offset + PRODUCT_LIMIT > product_count - 1:
        await callback.answer('Показан конец списка')
        return

    offset += PRODUCT_LIMIT

    await bot.edit_message_text(await get_products_str(callback.message.chat.id, offset),
                                callback.message.chat.id,
                                callback.message.message_id,
                                parse_mode='markdown',
                                reply_markup=build_pagination_kb('product'))
    await callback.answer()


async def view_product_prev(callback: types.CallbackQuery):
    global offset
    if offset == 0:
        await callback.answer('Показано начало списка')
        return

    offset -= PRODUCT_LIMIT
    if offset < 0:
        offset = 0

    await bot.edit_message_text(await get_products_str(callback.message.chat.id, offset),
                                callback.message.chat.id,
                                callback.message.message_id,
                                parse_mode='markdown',
                                reply_markup=build_pagination_kb('product'))
    await callback.answer()


def register_handlers(dispatcher: Dispatcher):
    dispatcher.register_callback_query_handler(view_product_next, text='next_product')
    dispatcher.register_callback_query_handler(view_product_prev, text='prev_product')
