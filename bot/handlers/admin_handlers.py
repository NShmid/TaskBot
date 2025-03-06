from aiogram import types, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from bot.filters.admin_filter import IsAdmin
from bot.utils.google_sheets import responsible_id, chat_id, set_image_id
from bot.keyboards import inline_keyboards
from bot.bot import bot


admin_router = Router()


class TaskForm(StatesGroup):
    image = State()          # Ввод картинки
    text = State()           # Ввод текста ТЗ
    responsible = State()    # Выбор ответственного
    deadline = State()       # Ввод дедлайна
    chat = State()           # Выбор чата
    confirm = State()        # Подтверждение ТЗ

messages_id = {}


@admin_router.message(Command("start"), IsAdmin(), StateFilter(None))
async def start_cmd_admin(message: types.Message, state: FSMContext):
    await message.answer(f"Привет, {message.from_user.first_name}! У тебя есть права "
                         f"администратора.\nЧтобы начать создание тз отправь картинку "
                         f"или напиши \'нет\'")
    await state.set_state(TaskForm.image)
    

@admin_router.message(IsAdmin(), TaskForm.image)
async def add_image(message: types.Message, state: FSMContext):
    if message.photo:
        await message.answer("Картинка сохранена.\nТеперь введи текст тз.")
        await state.update_data(image=message.photo[-1].file_id)
        await state.set_state(TaskForm.text)
    elif message.text and message.text.lower() == 'нет':
        await message.answer("Хорошо, картинки не будет.\nТеперь введи текст тз.")
        await state.set_state(TaskForm.text)
    else:
        await message.answer(f"Отправь картинку или напиши \'нет\' "
                             f"(для отмены создания тз напиши \'отмена\').")


@admin_router.message(IsAdmin(), TaskForm.text)
async def add_text(message: types.Message, state: FSMContext):
    if message.text:
        await state.update_data(text=message.text)
        sent_msg = await message.answer(f"Текст для тз сохранен. Теперь выбери ответственного:", 
                    reply_markup=inline_keyboards.get_responsible_keyboard(responsible_id))
        messages_id[message.chat.id] = sent_msg
        await state.set_state(TaskForm.responsible)
    else:
        await message.answer(f"Введи текст для тз. Для возврата на предыдущий шаг введи \'назад\'"
                             f" (для отмены создания тз напиши \'отмена\').")
        

@admin_router.callback_query(IsAdmin(), TaskForm.responsible)
async def add_responsible_inline(callback: types.CallbackQuery, state: FSMContext):
    choice = callback.data
    await messages_id[callback.message.chat.id].edit_reply_markup(reply_markup=None)
    await state.update_data(responsible=choice)
    await callback.message.answer(f"Ответственный назначен. Теперь введи дедлайн.")
    await state.set_state(TaskForm.deadline)


@admin_router.message(IsAdmin(), TaskForm.responsible)
async def add_responsible(message: types.Message, state: FSMContext):
    if message.text.isdigit() and message.text in responsible_id:
        await messages_id[message.chat.id].edit_reply_markup(reply_markup=None)
        await state.update_data(responsible=message.text)
        await message.answer(f"Ответственный назначен. Теперь введи дедлайн.")
        await state.set_state(TaskForm.deadline)
    else:
        await message.answer(f"Введи id ответственного из списка. Для возврата на предыдущий шаг"
                             f" введи \'назад\' (для отмены создания тз напиши \'отмена\').")


@admin_router.message(IsAdmin(), TaskForm.deadline)
async def add_deadline(message: types.Message, state: FSMContext):
    if message.text:
        await state.update_data(deadline=message.text)
        sent_msg = await message.answer(f"Дедлайн назначен. Выбери в какой чат отправить тз:", 
                             reply_markup=inline_keyboards.get_chats_keyboard(chat_id))
        messages_id[message.chat.id] = sent_msg
        await state.set_state(TaskForm.chat)
    else:
        await message.answer(f"Введи дедлайн текстом. Для возврата на предыдущий шаг введи"
                             f" \'назад\' (для отмены создания тз напиши \'отмена\').")


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
    await callback.message.answer(f"Если тз верно, введи \'отправить\'.")
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
        await message.answer(f"Если тз верно, введи \'отправить\'.")
        await state.set_state(TaskForm.confirm)
    else:
        await message.answer(f"Введи чат из списка. Для возврата на предыдущий шаг введи "
                             f" \'назад\' (для отмены создания тз напиши \'отмена\').")


@admin_router.message(IsAdmin(), TaskForm.confirm)
async def confirm(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отправить':
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
    else:
        await message.answer(f"Введи \'отправить\' если тз верное. Для возврата на предыдущий шаг "
                             f"введи \'назад\' (для отмены создания тз напиши \'отмена\').")

    
@admin_router.message(Command("start"))
async def start_cmd_user(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}! У тебя нет прав"
                         f" администратора.")


@admin_router.message()
async def start_cmd(message: types.Message):
    await message.answer("Для того, чтобы начать работу, напишите \'/start\'")