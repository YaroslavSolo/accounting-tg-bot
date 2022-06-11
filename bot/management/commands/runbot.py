from datetime import datetime

from django.core.management.base import BaseCommand
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.utils import executor

from orders.service import *
from bot.service import *
from bot.bot_init import bot, dispatcher
from bot.handlers import product_handlers, order_handlers, material_handlers, statistics_handlers, other_handlers


scheduler = AsyncIOScheduler()
job = None


async def process_notifications():
    print('Started processing notifications')

    notifications_count = await get_notifications_count()
    offset = 0
    batch_size = 100
    while offset < notifications_count:
        for user_id, order_id in await process_notifications_batch(offset, batch_size):
            await bot.send_message(user_id, '❗️ Менее чем через 5 часов наступает дедлайн заказа: ')
            await bot.send_message(user_id, await get_order_str(user_id, order_id), parse_mode='markdown')
        offset += batch_size

    print('Finished processing notifications')


def start_job():
    global job
    job = scheduler.add_job(process_notifications, 'interval', seconds=10)
    try:
        print('Scheduler started')
        scheduler.start()
    except Exception as ex:
        print(ex)


async def error_handler(update, error):
    if error is ValueError:
        pass
    else:
        print(error)
    return True


class Command(BaseCommand):
    help = 'Starts Telegram Bot'

    async def on_startup(self, _):
        self.stdout.write(self.style.SUCCESS('Telegram Bot started successfully'))
        self.stdout.write(self.style.SUCCESS(datetime.now()))

    async def on_shutdown(self, _):
        self.stdout.write(self.style.SUCCESS('Telegram Bot stopped successfully'))

    def handle(self, *args, **options):
        dispatcher.register_errors_handler(error_handler)
        other_handlers.register_handlers(dispatcher)
        product_handlers.register_handlers(dispatcher)
        order_handlers.register_handlers(dispatcher)
        material_handlers.register_handlers(dispatcher)
        statistics_handlers.register_handlers(dispatcher)

        start_job()

        executor.start_polling(
            dispatcher,
            skip_updates=True,
            on_startup=self.on_startup,
            on_shutdown=self.on_shutdown
        )