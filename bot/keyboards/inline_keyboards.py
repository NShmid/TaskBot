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


def get_deadline_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="Понедельник", callback_data="Понедельник"), InlineKeyboardButton(text="Вторник", callback_data="Вторник")],
        [InlineKeyboardButton(text="Среда", callback_data="Среда"), InlineKeyboardButton(text="Четверг", callback_data="Четверг")],
        [InlineKeyboardButton(text="Пятница", callback_data="Пятница"), InlineKeyboardButton(text="Суббота", callback_data="Суббота")],
        [InlineKeyboardButton(text="Воскресенье", callback_data="Воскресенье")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_confirm_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="Все верно", callback_data="Отправить"),
        InlineKeyboardButton(text="Исправить", callback_data="Исправить")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)