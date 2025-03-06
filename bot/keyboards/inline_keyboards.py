from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_responsible_keyboard(responsible_id):
    keyboard = [
        [InlineKeyboardButton(text=rid, callback_data=rid)] for rid in responsible_id
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_chats_keyboard(chat_id):
    keyboard = [
        [InlineKeyboardButton(text=rid, callback_data=rid)] for rid in chat_id
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)