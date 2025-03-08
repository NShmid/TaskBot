import asyncio

from aiogram import Dispatcher, types
from aiogram.fsm.strategy import FSMStrategy

from bot.bot import bot
from bot.handlers.admin_handlers import admin_router



dp = Dispatcher(fsm_strategy=FSMStrategy.USER_IN_CHAT)

dp.include_router(admin_router)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands([types.BotCommand(command='start', description='Создать тз')])
    await dp.start_polling(bot)
    

asyncio.run(main())