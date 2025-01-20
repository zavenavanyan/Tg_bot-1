
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
import asyncio
from datetime import datetime

# Токен бота
TOKEN = "7467870753:AAEhuZ42Qyd6YkqMVojBLS43LNDHJZZR5Io"

# Создаем объекты бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Хранилище задач
tasks = []

# Функция для добавления задачи
def add_task(task_text):
    task = {"text": task_text, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    tasks.append(task)

# Функция для формирования списка задач
def get_tasks():
    if not tasks:
        return "Список задач пуст."
    return "\n\n".join([f"{idx + 1}. {task['text']} (добавлено: {task['time']})" for idx, task in enumerate(tasks)])

# Функция для удаления задачи по индексу
def remove_task(index):
    try:
        del tasks[index - 1]
        return "Задача успешно удалена."
    except IndexError:
        return "Ошибка: задачи с таким номером не существует."

# Команда /start
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.answer(
        "Привет! Я помогу тебе управлять задачами. Перешли мне сообщение с задачей или используй кнопки.",
        reply_markup=main_menu()
    )

# Обработка пересланных сообщений
@dp.message_handler(lambda message: message.forward_date is not None)
async def handle_forwarded_message(message: types.Message):
    add_task(message.text)
    await message.answer("Задача добавлена!")

# Кнопки основного меню
def main_menu():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("📋 Показать задачи", callback_data="show_tasks"))
    keyboard.add(InlineKeyboardButton("➕ Добавить задачу", callback_data="add_task"))
    keyboard.add(InlineKeyboardButton("❌ Удалить задачу", callback_data="delete_task"))
    return keyboard

# Обработка кнопок
@dp.callback_query_handler(lambda c: c.data)
async def process_callback(callback_query: types.CallbackQuery):
    if callback_query.data == "show_tasks":
        await bot.send_message(callback_query.from_user.id, get_tasks())
    elif callback_query.data == "add_task":
        await bot.send_message(callback_query.from_user.id, "Отправь текст новой задачи.")
    elif callback_query.data == "delete_task":
        if not tasks:
            await bot.send_message(callback_query.from_user.id, "Список задач пуст.")
        else:
            task_list = "\n".join([f"{idx + 1}. {task['text']}" for idx, task in enumerate(tasks)])
            await bot.send_message(callback_query.from_user.id, f"Список задач:\n\n{task_list}\n\nНапиши номер задачи, которую хочешь удалить.")
    await callback_query.answer()

# Обработка текстовых сообщений (для добавления или удаления задачи)
@dp.message_handler(lambda message: not message.forward_date)
async def handle_text_message(message: types.Message):
    if message.text.isdigit():
        index = int(message.text)
        response = remove_task(index)
        await message.answer(response)
    else:
        add_task(message.text)
        await message.answer("Задача добавлена!")

# Периодическая отправка задач
async def scheduled_notifications():
    while True:
        now = datetime.now()
        if now.hour in [11, 20] and now.minute == 0:
            tasks_message = get_tasks()
            await bot.send_message(chat_id=bot._session._default_users[0], text=f"Напоминание о задачах:\n\n{tasks_message}")
        await asyncio.sleep(60)  # Ждать минуту перед следующим запуском

# Запуск планировщика
async def on_startup(dp):
    asyncio.create_task(scheduled_notifications())

# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
