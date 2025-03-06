from aiogram.filters import BaseFilter
from aiogram.types import Message
from utils.google_sheets import admins_id


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message):
        return str(message.from_user.id) in admins_id