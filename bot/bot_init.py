from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram import Bot

import os

bot = Bot(token=os.getenv('BOT_API_TOKEN'))
storage = MemoryStorage()
dispatcher = Dispatcher(bot, storage=storage)
