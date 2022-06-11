import datetime
from asgiref.sync import sync_to_async

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher.filters.state import State, StatesGroup


from orders.service import *
from products.service import *
from bot.service import *
from bot.bot_init import bot
from bot.validators.order_validators import *
from bot.validators.common_validators import *
from bot.keyboards import main_kb, build_order_edit_kb


cb = CallbackData('stub', 'id', 'action')


class OrderEditStates(StatesGroup):
    select_product = State()
    select_operation = State()
    save_changes = State()


async def edit_order(message: types.Message, state: FSMContext):
    await message.answer('Введите номер заказа')
    await state.finish()
    await OrderEditStates.select_product.set()


async def edit_selected_order_menu(message: types.Message):
    await validate_order_id(message)
    order_id = int(message.text)
    if await get_order(message.chat.id, order_id) is not None:
        await message.answer(await get_order_str(message.chat.id, order_id), parse_mode='markdown')
        await message.answer(
            '\nВыберите параметр для изменения',
            parse_mode='markdown',
            reply_markup=build_order_edit_kb(order_id)
        )
        await OrderEditStates.next()
    else:
        await message.answer('Заказ не найден. Пожалуйста, введите другой id заказа')


async def edit_selected_order_option(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    order_id = callback.data.split(':')[1]
    option = callback.data.split(':')[2]
    async with state.proxy() as data:
        data['id'] = order_id
        data['option'] = option

    message = ''
    if option == 'description':
        message = 'Введите новое описание'
    elif option == 'deadline_date':
        message = 'Введите новую дату дедлайна в формате дд.мм.гггг'
    elif option == 'deadline_time':
        message = 'Введите новое время дедлайна в формате чч:мм'

    await bot.send_message(callback.message.chat.id, message)
    await callback.answer('')
    await OrderEditStates.next()


async def edit_selected_order_option_save(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        order_id = data['id']
        option = data['option']

    order = await get_order(message.chat.id, order_id)

    if option == 'description':
        await validate_description(message)
        order.description = message.text
    elif option == 'deadline_date':
        await validate_date(message)
        new_deadline_date = datetime.datetime.strptime(message.text, '%d.%m.%Y')
        new_deadline_date = order.deadline_time.replace(
            day=new_deadline_date.day,
            month=new_deadline_date.month,
            year=new_deadline_date.year
        )
        order.deadline_time = new_deadline_date
        await save_notification_if_not_exists(order)
    elif option == 'deadline_time':
        await validate_deadline_time(message)
        new_deadline_time = datetime.datetime.strptime(message.text, '%H:%M')
        new_deadline_time = order.deadline_time.replace(
            hour=new_deadline_time.hour,
            minute=new_deadline_time.minute
        )
        order.deadline_time = new_deadline_time
        await save_notification_if_not_exists(order)

    await sync_to_async(order.save)()
    await message.answer('Изменения сохранены', reply_markup=main_kb)
    await state.finish()


async def delete_selected_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await delete_order(callback.message.chat.id, int(callback.data.split(':')[1]))
    await callback.message.answer('Заказ удален', reply_markup=main_kb)
    await callback.answer('Заказ удален')
    await state.finish()


async def finish_selected_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await finish_order(callback.message.chat.id, int(callback.data.split(':')[1]))
    await callback.message.answer('Заказ завершен', reply_markup=main_kb)
    await callback.answer('Заказ завершен')
    await state.finish()


async def cancel_selected_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await cancel_order(callback.message.chat.id, int(callback.data.split(':')[1]))
    await callback.message.answer('Заказ отменен', reply_markup=main_kb)
    await callback.answer('Заказ отменен')
    await state.finish()


def register_handlers(dispatcher: Dispatcher):
    dispatcher.register_message_handler(edit_selected_order_menu, state=OrderEditStates.select_product)
    dispatcher.register_callback_query_handler(
        edit_selected_order_option,
        cb.filter(action=['description', 'deadline_date', 'deadline_time']),
        state=OrderEditStates.select_operation
    )
    dispatcher.register_callback_query_handler(
        delete_selected_order,
        cb.filter(action=['delete_order']),
        state=OrderEditStates.select_operation
    )
    dispatcher.register_callback_query_handler(
        finish_selected_order,
        cb.filter(action=['finish']),
        state=OrderEditStates.select_operation
    )
    dispatcher.register_callback_query_handler(
        cancel_selected_order,
        cb.filter(action=['cancel']),
        state=OrderEditStates.select_operation
    )
    dispatcher.register_message_handler(edit_selected_order_option_save, state=OrderEditStates.save_changes)
