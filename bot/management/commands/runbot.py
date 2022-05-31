from datetime import datetime, timezone

from django.core.management.base import BaseCommand
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.utils import executor
from asgiref.sync import sync_to_async

from bot.models import DeadlineNotification
from bot.bot_init import bot, dispatcher
from bot.handlers import product_handlers, order_handlers, material_handlers, statistics_handlers, other_handlers


scheduler = AsyncIOScheduler()
job = None


async def notify():
    print('Notify job started')
    # notifications = await sync_to_async(DeadlineNotification.objects.all)()
    # for notification in notifications:
    #     if notification.user_id.notifications_enabled and datetime.now().replace(tzinfo=timezone.utc) > notification.order.deadline_time.replace(tzinfo=timezone.utc):
    #         await bot.send_message(notification.user_id, '')
    #     notification.delete()
    await bot.send_message(717389478, '')

    print('Notify job finished')


def start_job():
    global job
    job = scheduler.add_job(notify, 'interval', seconds=10)
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
        # dispatcher.register_errors_handler(error_handler)
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