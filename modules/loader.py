import logging
from aiogram import Bot, Dispatcher, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from modules.database import storage

# Подключение API Telegram.
print('Подключение API Telegram...')
bot = Bot(token = '', parse_mode = types.ParseMode.HTML)
dp = Dispatcher(bot, storage = storage)
scheduler = AsyncIOScheduler()

# Подключение логгирования.
print('Подключение логгирования...')
logging.basicConfig(filename='data/bot.log', format='[%(levelname)s] %(asctime)s - %(message)s', datefmt='%d/%b/%y %H:%M:%S')