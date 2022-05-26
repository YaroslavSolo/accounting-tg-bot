from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from materials.service import *
from bot.bot_init import bot, dispatcher
from bot.keyboards import main_kb, build_pagination_kb


offset = 0


async def view_material(message: types.Message, state: FSMContext):
    global offset
    offset = 0
    await state.finish()
    await message.answer(f'Всего материалов: {await get_materials_count(message.chat.id)}', reply_markup=main_kb)
    await message.answer(
        await get_materials_str(message.chat.id, offset),
        parse_mode='markdown',
        reply_markup=build_pagination_kb('material')
    )


async def view_material_next(callback: types.CallbackQuery):
    global offset
    product_count = await get_materials_count(callback.message.chat.id)
    if offset + MATERIAL_LIMIT > product_count - 1:
        await callback.answer('Показан конец списка')
        return

    offset += MATERIAL_LIMIT

    await bot.edit_message_text(await get_materials_str(callback.message.chat.id, offset),
                                callback.message.chat.id,
                                callback.message.message_id,
                                parse_mode='markdown',
                                reply_markup=build_pagination_kb('material'))
    await callback.answer()


async def view_material_prev(callback: types.CallbackQuery):
    global offset
    if offset == 0:
        await callback.answer('Показано начало списка')
        return

    offset -= MATERIAL_LIMIT
    if offset < 0:
        offset = 0

    await bot.edit_message_text(await get_materials_str(callback.message.chat.id, offset),
                                callback.message.chat.id,
                                callback.message.message_id,
                                parse_mode='markdown',
                                reply_markup=build_pagination_kb('material'))
    await callback.answer()


def register_handlers(dispatcher: Dispatcher):
    dispatcher.register_callback_query_handler(view_material_next, text='next_material')
    dispatcher.register_callback_query_handler(view_material_prev, text='prev_material')
