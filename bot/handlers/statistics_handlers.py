import datetime
import os

from aiogram import types, Dispatcher
from aiogram.types import InputFile
from aiogram.dispatcher import FSMContext

from bot.bot_init import bot
from bot.statistics import *
from bot.handlers.other_handlers import MenuKeyboardStates
from bot.validators.common_validators import *
from bot.keyboards.common import partition_type_kb, main_kb


async def statistics_period_start(message: types.Message, state: FSMContext):
    await validate_date(message)
    async with state.proxy() as order:
        period_start = datetime.datetime.strptime(message.text, '%d.%m.%Y')
        order['period_start'] = period_start
    await MenuKeyboardStates.next()
    await message.answer('Введите дату окончания периода:')


async def statistics_period_end(message: types.Message, state: FSMContext):
    await validate_date(message)
    async with state.proxy() as order:
        period_end = datetime.datetime.strptime(message.text, '%d.%m.%Y')
        order['period_end'] = period_end
        period_start = order['period_start']

    if period_start > period_end:
        await message.answer('Дата окончания предшествует дате начала\nПожалуйста, укажите более позднюю дату')
        return

    await message.answer('Выберите размер разбиения:', reply_markup=partition_type_kb)
    await MenuKeyboardStates.next()


async def statistics_select_partition(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as order:
        period_end = order['period_end']
        period_start = order['period_start']

    period_start_str = period_start.strftime('%d.%m.%Y')
    period_end_str = period_end.strftime('%d.%m.%Y')
    order_data = await prepare_order_data(callback.message.chat.id, period_start, period_end)

    await callback.message.answer(
        f'📊 Статистика за период *{period_start_str}* - *{period_end_str}*\n\n'
        f'{get_overall_stats(order_data)}',
        parse_mode='markdown',
        reply_markup=main_kb
    )

    chat_id = callback.message.chat.id
    graph_filenames = [
        f'pictures_tmp/graph1_{chat_id}.png',
        f'pictures_tmp/graph2_{chat_id}.png',
        f'pictures_tmp/graph3_{chat_id}.png',
        f'pictures_tmp/graph4_{chat_id}.png',
    ]

    plot_revenue_trend(graph_filenames[0], order_data, callback.data)
    plot_num_orders_trend(graph_filenames[1], order_data, callback.data)
    plot_avg_order_sum_trend(graph_filenames[2], order_data, callback.data)
    plot_product_popularity_trend(
        graph_filenames[3],
        await get_product_ids_and_names(chat_id),
        await get_products_for_orders(order_data.id)
    )

    media = types.MediaGroup()
    for filename in graph_filenames:
        media.attach_photo(InputFile(filename))

    await bot.send_media_group(chat_id, media=media)

    for filename in graph_filenames:
        os.remove(filename)

    await state.finish()


def register_handlers(dispatcher: Dispatcher):
    dispatcher.register_message_handler(statistics_period_start, state=MenuKeyboardStates.statistics_period_start)
    dispatcher.register_message_handler(statistics_period_end, state=MenuKeyboardStates.statistics_period_end)
    dispatcher.register_callback_query_handler(
        statistics_select_partition,
        state=MenuKeyboardStates.statistics_select_partition
    )
