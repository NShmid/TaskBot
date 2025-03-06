import os
from dotenv import find_dotenv, load_dotenv

from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode


load_dotenv(find_dotenv())

bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)