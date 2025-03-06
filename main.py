import os
import asyncio
from dotenv import find_dotenv, load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.fsm.strategy import FSMStrategy

from handlers.admin_handlers import admin_router


load_dotenv(find_dotenv())

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(fsm_strategy=FSMStrategy.USER_IN_CHAT)

dp.include_router(admin_router)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    

asyncio.run(main())