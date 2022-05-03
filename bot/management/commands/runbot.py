from django.core.management.base import BaseCommand

from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram import Bot

import os

from bot.handlers import echo, common


class Command(BaseCommand):
    help = 'Starts Telegram Bot'

    async def on_startup(self, _):
        self.stdout.write(self.style.SUCCESS('Telegram Bot started successfully'))

    async def on_shutdown(self, _):
        self.stdout.write(self.style.SUCCESS('Telegram Bot stopped successfully'))

    def handle(self, *args, **options):
        bot = Bot(token=os.getenv('BOT_API_TOKEN'))
        dispatcher = Dispatcher(bot)

        echo.register_handlers(dispatcher)
        common.register_handlers(dispatcher)

        executor.start_polling(
            dispatcher,
            skip_updates=True,
            on_startup=self.on_startup,
            on_shutdown=self.on_shutdown
        )
