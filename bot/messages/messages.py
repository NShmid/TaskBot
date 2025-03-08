from bot.utils.google_sheets import chat_id, responsible_id


IMAGE_START = (f"Чтобы начать создание тз отправь картинку или напиши"
    f"\'нет\', если картинки не будет.")
IMAGE_CANCEL = f"Отправь картинку заново или напиши \'нет\', если картинки не будет."

TEXT_CANCEL = f"Напиши текст для тз заново."

RESPONSIBLE_START = f"Теперь выбери ответсвенного. Вот список ответсвтвенных:\n" + ', '.join(responsible_id) + '.'
RESPONSIBLE_CANCEL = f"Выбери ответсвенного за тз заново. Вот список ответсвтвенных:\n" + ', '.join(responsible_id) + '.'

DEADLINE_CANCEL = f"Напиши дедлайн для тз заново."

CHAT_START = f"Выбери в какой чат отправить тз. Список чатов:\n" + ', '.join(chat_id) + '.'
CHAT_CANCEL = f"Выбери в какой чат отправить тз заново. Список чатов:\n" + ', '.join(chat_id) + '.'