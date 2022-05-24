from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from orders.service import *
from bot.bot_init import bot, dispatcher
from bot.keyboards.common import main_kb, build_pagination_kb


offset = 0


async def view_order(message: types.Message, state: FSMContext):
    global offset
    offset = 0
    await state.finish()
    await message.answer(
        f'Всего активных заказов: {await get_active_orders_count(message.chat.id)}',
        reply_markup=main_kb
    )
    await message.answer(
        await get_active_orders_str(message.chat.id, 0),
        parse_mode='markdown',
        reply_markup=build_pagination_kb('order')
    )


async def view_order_next(callback: types.CallbackQuery):
    global offset
    product_count = await get_active_orders_count(callback.message.chat.id)
    if offset + ORDER_LIMIT > product_count - 1:
        await callback.answer('Показан конец списка')
        return

    offset += ORDER_LIMIT

    await bot.edit_message_text(await get_active_orders_str(callback.message.chat.id, offset),
                                callback.message.chat.id,
                                callback.message.message_id,
                                parse_mode='markdown',
                                reply_markup=build_pagination_kb('order'))
    await callback.answer()


async def view_order_prev(callback: types.CallbackQuery):
    global offset
    if offset == 0:
        await callback.answer('Показано начало списка')
        return

    offset -= ORDER_LIMIT
    if offset < 0:
        offset = 0

    await bot.edit_message_text(await get_active_orders_str(callback.message.chat.id, offset),
                                callback.message.chat.id,
                                callback.message.message_id,
                                parse_mode='markdown',
                                reply_markup=build_pagination_kb('order'))
    await callback.answer()


def register_handlers(dispatcher: Dispatcher):
    dispatcher.register_callback_query_handler(view_order_next, text='next_order')
    dispatcher.register_callback_query_handler(view_order_prev, text='prev_order')
