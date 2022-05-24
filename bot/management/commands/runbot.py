from django.core.management.base import BaseCommand

from aiogram.utils import executor

from bot.bot_init import bot, dispatcher
from bot.handlers import product_handlers, order_handlers, statistics_handlers, other_handlers


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

    async def on_shutdown(self, _):
        self.stdout.write(self.style.SUCCESS('Telegram Bot stopped successfully'))

    def handle(self, *args, **options):
        # dispatcher.register_errors_handler(error_handler)
        other_handlers.register_handlers(dispatcher)
        product_handlers.register_handlers(dispatcher)
        order_handlers.register_handlers(dispatcher)
        statistics_handlers.register_handlers(dispatcher)

        executor.start_polling(
            dispatcher,
            skip_updates=True,
            on_startup=self.on_startup,
            on_shutdown=self.on_shutdown
        )
