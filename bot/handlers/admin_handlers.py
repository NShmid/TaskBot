from aiogram import types, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from bot.filters.admin_filter import IsAdmin
from bot.utils.google_sheets import responsible_id, chat_id, set_image_id
from bot.keyboards import inline_keyboards
from bot.bot import bot
from bot.messages import messages


admin_router = Router()


class TaskForm(StatesGroup):
    image = State()          # Ввод картинки
    text = State()           # Ввод текста ТЗ
    responsible = State()    # Выбор ответственного
    deadline = State()       # Ввод дедлайна
    chat = State()           # Выбор чата
    confirm = State()        # Подтверждение ТЗ
    

messages_id = {}
text = {
    'TaskForm:image': messages.IMAGE_CANCEL,
    'TaskForm:text': messages.TEXT_CANCEL,
    'TaskForm:responsible': messages.RESPONSIBLE_CANCEL,
    'TaskForm:deadline': messages.DEADLINE_CANCEL,
    'TaskForm:chat': messages.CHAT_CANCEL
}

keyboards = {
    'TaskForm:image': None,
    'TaskForm:text': None,
    'TaskForm:responsible': inline_keyboards.get_responsible_keyboard(responsible_id),
    'TaskForm:deadline': inline_keyboards.get_deadline_keyboard(),
    'TaskForm:chat': inline_keyboards.get_chats_keyboard(chat_id)
}


@admin_router.message(Command("start"), IsAdmin(), StateFilter(None))
async def start_cmd_admin(message: types.Message, state: FSMContext):
    await message.answer(f"Привет, {message.from_user.first_name}! У тебя есть права "
                         f"администратора.\n{messages.IMAGE_START}")
    await state.set_state(TaskForm.image)
    

@admin_router.message(StateFilter('*'), F.text.lower() == "назад")
async def cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state == TaskForm.image:
        await message.answer("Предыдущего шага нет.")
        return

    prev_state = None
    answer = ''
    for step in TaskForm.__all_states__:
        if step.state == current_state:
            await state.set_state(prev_state)
            break
        prev_state = step
    
    answer = f"Вы вернулись на предыдущий шаг.\n{text[prev_state.state]}"
    
    # Удаляем клавиатуру если она была
    if message.chat.id in messages_id:
        await messages_id[message.chat.id].edit_reply_markup(reply_markup=None)
    
    # Создаем новую клавиатуру с сообщением
    sent_msg = await message.answer(answer, reply_markup=keyboards[prev_state.state])
    messages_id[message.chat.id] = sent_msg
    
    return
    

@admin_router.message(IsAdmin(), TaskForm.image)
async def add_image(message: types.Message, state: FSMContext):
    if message.photo:
        await message.answer("Картинка сохранена.\nТеперь введи текст тз.")
        await state.update_data(image=message.photo[-1].file_id)
        await state.set_state(TaskForm.text)
    elif message.text and message.text.lower() == 'нет':
        await message.answer(f"Хорошо, картинки не будет.\nТеперь введи текст тз."
                             f"\nДля возврата на предыдущий шаг введи \'назад\'")
        await state.set_state(TaskForm.text)
    else:
        await message.answer(f"Отправь картинку или напиши \'нет\'")


@admin_router.message(IsAdmin(), TaskForm.text)
async def add_text(message: types.Message, state: FSMContext):
    if message.text:
        await state.update_data(text=message.text)
        sent_msg = await message.answer(f"Текст для тз сохранен. {messages.RESPONSIBLE_START}."
                                        f"\nДля возврата на предыдущий шаг введи \'назад\'", 
                    reply_markup=inline_keyboards.get_responsible_keyboard(responsible_id))
        messages_id[message.chat.id] = sent_msg
        await state.set_state(TaskForm.responsible)
    else:
        await message.answer(f"Введи текст для тз.\nДля возврата на предыдущий шаг введи \'назад\'")
        

@admin_router.callback_query(IsAdmin(), TaskForm.responsible)
async def add_responsible_inline(callback: types.CallbackQuery, state: FSMContext):
    choice = callback.data
    await messages_id[callback.message.chat.id].edit_reply_markup(reply_markup=None)
    await state.update_data(responsible=choice)
    sent_msg = await callback.message.answer(f"Ответственный назначен. Теперь введи дедлайн."
                                             f"\nДля возврата на предыдущий шаг введи \'назад\'",
            reply_markup=inline_keyboards.get_deadline_keyboard())
    messages_id[callback.message.chat.id] = sent_msg
    await state.set_state(TaskForm.deadline)


@admin_router.message(IsAdmin(), TaskForm.responsible)
async def add_responsible(message: types.Message, state: FSMContext):
    if message.text.isdigit() and message.text in responsible_id:
        await messages_id[message.chat.id].edit_reply_markup(reply_markup=None)
        await state.update_data(responsible=message.text)
        sent_msg = await message.answer(f"Ответственный назначен. Теперь введи дедлайн."
                                        f"\nДля возврата на предыдущий шаг введи \'назад\'",
                reply_markup=inline_keyboards.get_deadline_keyboard())
        messages_id[message.chat.id] = sent_msg
        await state.set_state(TaskForm.deadline)
    else:
        await message.answer(f"Введи id ответственного из списка."
                             f"\nДля возврата на предыдущий шаг введите \'назад\'.")


@admin_router.callback_query(IsAdmin(), TaskForm.deadline)
async def add_deadline_inline(callback: types.CallbackQuery, state: FSMContext):
    await messages_id[callback.message.chat.id].edit_reply_markup(reply_markup=None)

    await state.update_data(deadline=callback.data)
    sent_msg = await callback.message.answer(f"Дедлайн назначен. {messages.CHAT_START}."
                                             f"\nДля возврата на предыдущий шаг введи \'назад\'", 
                            reply_markup=inline_keyboards.get_chats_keyboard(chat_id))
    messages_id[callback.message.chat.id] = sent_msg
    await state.set_state(TaskForm.chat)


@admin_router.message(IsAdmin(), TaskForm.deadline)
async def add_deadline(message: types.Message, state: FSMContext):
    if message.text:
        await messages_id[message.chat.id].edit_reply_markup(reply_markup=None)
        await state.update_data(deadline=message.text)
        sent_msg = await message.answer(f"Дедлайн назначен. {messages.CHAT_START}."
                                        f"\nДля возврата на предыдущий шаг введи \'назад\'", 
                             reply_markup=inline_keyboards.get_chats_keyboard(chat_id))
        messages_id[message.chat.id] = sent_msg
        await state.set_state(TaskForm.chat)
    else:
        await message.answer(f"Введи дедлайн текстом. Для возврата на предыдущий шаг введите \'назад\'.")


@admin_router.callback_query(IsAdmin(), TaskForm.chat)
async def add_chat_inline(callback: types.CallbackQuery, state: FSMContext):
    choice = callback.data
    await messages_id[callback.message.chat.id].edit_reply_markup(reply_markup=None)
    await state.update_data(chat=choice)
    data = await state.get_data()
    await callback.message.answer(f"Чат выбран. Проверим тз:")
    caption = (
            f"<b>Текст:</b> {data.get('text')} \n"
            f"<b>Ответственный:</b> {data.get('responsible')} \n"
            f"<b>Дедлайн:</b> {data.get('deadline')} \n"
            f"<b>Чат:</b> {data.get('chat')} \n")
    if "image" in data:
        await callback.message.answer_photo(data.get("image"), caption=caption)
    else:
        await callback.message.answer(caption)
    sent_msg = await callback.message.answer(f"Если тз верно, введи \'отправить\' или нажми на кнопку \'Все верно\'."
                                             f"\nДля возврата на предыдущий шаг введи \'назад\'", 
            reply_markup=inline_keyboards.get_confirm_keyboard())
    messages_id[callback.message.chat.id] = sent_msg
    await state.set_state(TaskForm.confirm)
    

@admin_router.message(IsAdmin(), TaskForm.chat)
async def add_chat(message: types.Message, state: FSMContext):
    if message.text.isdigit() and message.text in chat_id:
        await messages_id[message.chat.id].edit_reply_markup(reply_markup=None)
        await state.update_data(chat=message.text)
        data = await state.get_data()
        await message.answer(f"Чат выбран. Проверим тз:")
        caption = (
            f"<b>Текст:</b> {data.get('text')} \n"
            f"<b>Ответственный:</b> {data.get('responsible')} \n"
            f"<b>Дедлайн:</b> {data.get('deadline')} \n"
            f"<b>Чат:</b> {data.get('chat')} \n")
        if "image" in data:
            await message.answer_photo(data.get("image"), caption=caption)
        else:
            await message.answer(caption)
        sent_msg = await message.answer(f"Если тз верно, введи \'отправить\' или нажми на кнопку \'Все верно\'."
                                        f"\nДля возврата на предыдущий шаг введи \'назад\'.", 
                reply_markup=inline_keyboards.get_confirm_keyboard())
        messages_id[message.chat.id] = sent_msg
        await state.set_state(TaskForm.confirm)
    else:
        await message.answer(f"Введи чат из списка. Для возврата на предыдущий шаг введи \'назад\'")


@admin_router.callback_query(IsAdmin(), TaskForm.confirm)
async def confirm_inline(callback: types.CallbackQuery, state: FSMContext):
    await messages_id[callback.message.chat.id].edit_reply_markup(reply_markup=None)
    choice = callback.data
    if choice.lower() == "отправить":
        data = await state.get_data()
        set_image_id(data.get("image"))
        
        caption = (
            f"<b>Задание:</b> {data.get('text')} \n"
            f"<b>Ответственный:</b> {data.get('responsible')} \n"
            f"<b>Дедлайн:</b> {data.get('deadline')} \n")
        chat_id = data.get("chat")
        if "image" in data:
            await bot.send_photo(chat_id=chat_id, photo=data.get("image"), caption=caption)
        else:
            await bot.send_message(chat_id=chat_id, text=caption)
            
        await callback.message.answer("Тз успешно отправлено!")
        await state.clear()
    elif choice.lower() == "исправить":
        await callback.message.answer(f"Хорошо, начнем заполнение тз заново.{messages.IMAGE_START}."
                                      f"\nДля возврата на предыдущий шаг введи \'назад\' ")
        await state.set_state(TaskForm.image)
        
    
@admin_router.message(IsAdmin(), TaskForm.confirm)
async def confirm(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отправить':
        await messages_id[message.chat.id].edit_reply_markup(reply_markup=None)
        data = await state.get_data()
        set_image_id(data.get("image"))
        
        caption = (
            f"<b>Задание:</b> {data.get('text')} \n"
            f"<b>Ответственный:</b> {data.get('responsible')} \n"
            f"<b>Дедлайн:</b> {data.get('deadline')} \n")
        chat_id = data.get("chat")
        if "image" in data:
            await bot.send_photo(chat_id=chat_id, photo=data.get("image"), caption=caption)
        else:
            await bot.send_message(chat_id=chat_id, text=caption)
            
        await message.answer("Тз успешно отправлено!")
        await state.clear()
    elif message.text.lower() == "исправить":
        await message.answer(f"Хорошо, начнем заполнение тз заново.{messages.IMAGE_START}")
        await state.set_state(TaskForm.image)
    else:
        await message.answer(f"Введи \'отправить\' если тз верное. Для возврата на предыдущий шаг введи \'назад\'.")

    
@admin_router.message(Command("start"))
async def start_cmd_user(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}! У тебя нет прав"
                         f" администратора.")


@admin_router.message()
async def start_cmd(message: types.Message):
    await message.answer("Для того, чтобы начать работу, напишите \'/start\'")