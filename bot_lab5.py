import logging
import asyncio
import os

from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import psycopg2

# Загрузка API токена из .env
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# Подключение к новой базе данных
def get_connection():
    return psycopg2.connect(
        dbname="currency_bot",
        user="currency_user",
        password="currency_pass",
        host="localhost",
        port=5432
    )


# Проверка: является ли пользователь админом
def is_admin(chat_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM admins WHERE chat_id = %s;", (str(chat_id),))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None


# FSM состояния
class CurrencyForm(StatesGroup):
    name = State()
    rate = State()
    delete = State()
    update_name = State()
    update_rate = State()


class ConvertForm(StatesGroup):
    currency = State()
    amount = State()


# /start
@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я бот для конвертации валют.\n"
        "Команды:\n"
        "/get_currencies – список валют\n"
        "/convert – перевести в рубли\n"
        "/manage_currency – управление (для админов)"
    )


# /me (показывает chat_id)
@dp.message(Command("me"))
async def cmd_me(message: Message) -> None:
    await message.answer(f"Твой chat_id: {message.chat.id}")


# /get_currencies
@dp.message(Command("get_currencies"))
async def cmd_get_currencies(message: Message) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT currency_name, rate FROM currencies;")
        rows = cursor.fetchall()

        if not rows:
            await message.answer("Список валют пуст.")
            return

        text = "Валюты:\n"
        for name, rate in rows:
            text += f"• {name.upper()} = {rate} RUB\n"

        await message.answer(text)
    finally:
        cursor.close()
        conn.close()


# /convert
@dp.message(Command("convert"))
async def cmd_convert(message: Message, state: FSMContext) -> None:
    await message.answer("Введите название валюты:")
    await state.set_state(ConvertForm.currency)


@dp.message(ConvertForm.currency)
async def process_convert_currency(message: Message, state: FSMContext) -> None:
    currency = message.text.strip().lower()

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT rate FROM currencies WHERE currency_name = %s;",
            (currency,)
        )
        result = cursor.fetchone()

        if result is None:
            await message.answer("Валюта не найдена.")
            await state.clear()
            return

        rate = result[0]
        await state.update_data(currency_name=currency, rate=rate)
        await message.answer(f"Введите сумму в {currency.upper()}:")
        await state.set_state(ConvertForm.amount)

    finally:
        cursor.close()
        conn.close()


@dp.message(ConvertForm.amount)
async def process_convert_amount(message: Message, state: FSMContext) -> None:
    try:
        amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Ошибка: введите корректное число.")
        return

    data = await state.get_data()
    currency = data.get("currency_name")
    rate = data.get("rate")

    if currency is None or rate is None:
        await message.answer("Ошибка: данные утеряны, начните заново командой /convert.")
        await state.clear()
        return

    result = amount * float(rate)

    await message.answer(
        f"{amount} {currency.upper()} = {result:.2f} RUB "
        f"(по курсу 1 {currency.upper()} = {rate} RUB)"
    )
    await state.clear()


# /manage_currency
@dp.message(Command("manage_currency"))
async def cmd_manage_currency(message: Message) -> None:
    if not is_admin(str(message.chat.id)):
        await message.answer("⛔ Доступ только для админов.")
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Добавить валюту"),
                KeyboardButton(text="Удалить валюту"),
                KeyboardButton(text="Изменить курс валюты")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer("Выберите действие:", reply_markup=keyboard)


# Добавить валюту
@dp.message(F.text == "Добавить валюту")
async def handle_add_currency_button(message: Message, state: FSMContext):
    await message.answer("Введите название валюты:")
    await state.set_state(CurrencyForm.name)


@dp.message(CurrencyForm.name)
async def process_currency_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip().lower()

    # Проверка существования валюты
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM currencies WHERE currency_name = %s;", (name,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        await message.answer("Данная валюта уже существует.")
        await state.clear()
        return

    await state.update_data(currency_name=name)
    await message.answer("Теперь введите курс к рублю:")
    await state.set_state(CurrencyForm.rate)


@dp.message(CurrencyForm.rate)
async def process_currency_rate(message: Message, state: FSMContext) -> None:
    try:
        rate = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Ошибка: введите корректное число.")
        return

    data = await state.get_data()
    name = data.get("currency_name")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO currencies (currency_name, rate) VALUES (%s, %s);",
            (name, rate)
        )
        conn.commit()
        await message.answer(f"Сохранено: 1 {name.upper()} = {rate} RUB")
    except Exception as e:
        conn.rollback()
        await message.answer(f"Ошибка: {e}")
    finally:
        cursor.close()
        conn.close()
        await state.clear()


# Удалить валюту
@dp.message(F.text == "Удалить валюту")
async def handle_delete_currency(message: Message, state: FSMContext):
    await message.answer("Введите название валюты, которую нужно удалить:")
    await state.set_state(CurrencyForm.delete)


@dp.message(CurrencyForm.delete)
async def process_delete_currency(message: Message, state: FSMContext):
    name = message.text.strip().lower()

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM currencies WHERE currency_name = %s;", (name,))
        if cursor.rowcount == 0:
            await message.answer("Валюта не найдена.")
        else:
            conn.commit()
            await message.answer(f"Валюта {name.upper()} удалена.")
    finally:
        cursor.close()
        conn.close()
        await state.clear()


# Обновить курс валюты
@dp.message(F.text == "Изменить курс валюты")
async def handle_update_currency(message: Message, state: FSMContext):
    await message.answer("Введите название валюты, курс которой нужно изменить:")
    await state.set_state(CurrencyForm.update_name)


@dp.message(CurrencyForm.update_name)
async def process_update_name(message: Message, state: FSMContext):
    await state.update_data(currency_name=message.text.strip().lower())
    await message.answer("Введите новый курс этой валюты:")
    await state.set_state(CurrencyForm.update_rate)


@dp.message(CurrencyForm.update_rate)
async def process_update_rate(message: Message, state: FSMContext):
    try:
        new_rate = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Ошибка: введите корректное число.")
        return

    data = await state.get_data()
    name = data.get("currency_name")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE currencies SET rate = %s WHERE currency_name = %s;", (new_rate, name))
        if cursor.rowcount == 0:
            await message.answer("Валюта не найдена.")
        else:
            conn.commit()
            await message.answer(f"Курс валюты {name.upper()} обновлён: {new_rate} RUB")
    finally:
        cursor.close()
        conn.close()
        await state.clear()


# Установка команд по ролям
async def set_commands():
    admin_commands = [
        BotCommand(command="start", description="Начать работу"),
        BotCommand(command="manage_currency", description="Управление валютами"),
        BotCommand(command="get_currencies", description="Показать список валют"),
        BotCommand(command="convert", description="Конвертировать валюту")
    ]

    user_commands = [
        BotCommand(command="start", description="Начать работу"),
        BotCommand(command="get_currencies", description="Показать список валют"),
        BotCommand(command="convert", description="Конвертировать валюту")
    ]

    admin_id = 1291190562
    await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=admin_id))
    await bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())


# Запуск бота
async def main():
    await set_commands()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
