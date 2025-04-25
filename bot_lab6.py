import logging
import asyncio
import os
import aiohttp

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, BotCommand, BotCommandScopeChat, BotCommandScopeDefault
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

# Загрузка API токена из .env
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Проверка роли через микросервис
async def is_admin(chat_id: int) -> bool:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"http://localhost:5003/is_admin/{chat_id}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    logging.info(f"Роль пользователя {chat_id}: {data.get('is_admin')}")
                    return data.get("is_admin", False)
        except:
            return False
    return False

# Состояния для команды /convert
class ConvertForm(StatesGroup):
    currency = State()
    amount = State()


# Состояния для /manage_currency
class ManageCurrencyForm(StatesGroup):
    name = State()
    rate = State()
    delete = State()
    update_name = State()
    update_rate = State()


# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Я бот для конвертации валют.\nКоманды:\n/get_currencies — список валют\n/convert — пересчитать сумму в рубли\n/manage_currency — управление валютами")


# Команда /get_currencies — запрос к data_service
@dp.message(Command("get_currencies"))
async def cmd_get_currencies(message: Message):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("http://localhost:5002/currencies") as response:
                if response.status == 200:
                    data = await response.json()
                    if not data:
                        await message.answer("Список валют пуст.")
                        return
                    text = "Валюты:\n"
                    for item in data:
                        text += f"• {item['currency_name'].upper()} = {item['rate']} RUB\n"
                    await message.answer(text)
                else:
                    await message.answer(f"Ошибка при запросе: {response.status}")
        except Exception as e:
            await message.answer(f"Ошибка соединения с сервисом: {e}")


# Команда /convert — пошаговая FSM логика
@dp.message(Command("convert"))
async def cmd_convert(message: Message, state: FSMContext):
    await message.answer("Введите название валюты:")
    await state.set_state(ConvertForm.currency)


@dp.message(ConvertForm.currency)
async def process_currency_name(message: Message, state: FSMContext):
    await state.update_data(currency_name=message.text.strip().lower())
    await message.answer("Введите сумму в выбранной валюте:")
    await state.set_state(ConvertForm.amount)


@dp.message(ConvertForm.amount)
async def process_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Ошибка: введите корректное число.")
        return

    data = await state.get_data()
    currency_name = data.get("currency_name")
    url = f"http://localhost:5002/convert?currency_name={currency_name}&amount={amount}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    await message.answer(
                        f"{result['amount']} {result['currency_name'].upper()} = {result['converted_to_rub']} RUB\n"
                        f"(по курсу {result['rate']} RUB)"
                    )
                elif response.status == 404:
                    await message.answer("Валюта не найдена.")
                else:
                    await message.answer(f"Ошибка при конвертации: {response.status}")
        except Exception as e:
            await message.answer(f"Ошибка соединения с сервисом: {e}")
    await state.clear()


# Команда /manage_currency
@dp.message(Command("manage_currency"))
async def cmd_manage_currency(message: Message):
    # Логирование запроса на проверку роли
    logging.info(f"Проверка роли пользователя: {message.from_user.id}")
    if not await is_admin(message.from_user.id):
        await message.answer("⛔ Эта команда доступна только администраторам.")
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



# Защита кнопок от обычных пользователей
@dp.message(F.text == "Добавить валюту")
async def handle_add_currency_button(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        await message.answer("⛔ Кнопка доступна только администраторам.")
        return
    await message.answer("Введите название валюты:")
    await state.set_state(ManageCurrencyForm.name)

@dp.message(ManageCurrencyForm.name)
async def process_add_name(message: Message, state: FSMContext):
    name = message.text.strip().lower()
    await state.update_data(currency_name=name)
    await message.answer("Введите курс к рублю:")
    await state.set_state(ManageCurrencyForm.rate)


@dp.message(ManageCurrencyForm.rate)
async def process_add_rate(message: Message, state: FSMContext):
    try:
        rate = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Ошибка: введите корректный курс.")
        return

    data = await state.get_data()
    currency_name = data.get("currency_name")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post("http://localhost:5001/load", json={"currency_name": currency_name, "rate": rate}) as resp:
                if resp.status == 201:
                    await message.answer(f"Валюта {currency_name.upper()} успешно добавлена.")
                elif resp.status == 409:
                    await message.answer("Данная валюта уже существует.")
                else:
                    await message.answer(f"Ошибка при добавлении: {resp.status}")
        except Exception as e:
            await message.answer(f"Ошибка соединения с currency-manager: {e}")
    await state.clear()


# Удалить валюту
@dp.message(F.text == "Удалить валюту")
async def handle_delete_currency(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        await message.answer("⛔ Кнопка доступна только администраторам.")
        return
    await message.answer("Введите название валюты:")
    await state.set_state(ManageCurrencyForm.delete)


@dp.message(ManageCurrencyForm.delete)
async def process_delete(message: Message, state: FSMContext):
    name = message.text.strip().lower()
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post("http://localhost:5001/delete", json={"currency_name": name}) as resp:
                if resp.status == 200:
                    await message.answer(f"Валюта {name.upper()} удалена.")
                elif resp.status == 404:
                    await message.answer("Валюта не найдена.")
                else:
                    await message.answer(f"Ошибка при удалении: {resp.status}")
        except Exception as e:
            await message.answer(f"Ошибка соединения с currency-manager: {e}")
    await state.clear()


# Изменить курс валюты
@dp.message(F.text == "Изменить курс валюты")
async def handle_update_currency(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        await message.answer("⛔ Кнопка доступна только администраторам.")
        return
    await message.answer("Введите название валюты:")
    await state.set_state(ManageCurrencyForm.update_name)


@dp.message(ManageCurrencyForm.update_name)
async def process_update_name(message: Message, state: FSMContext):
    await state.update_data(currency_name=message.text.strip().lower())
    await message.answer("Введите новый курс:")
    await state.set_state(ManageCurrencyForm.update_rate)


@dp.message(ManageCurrencyForm.update_rate)
async def process_update_rate(message: Message, state: FSMContext):
    try:
        rate = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Ошибка: введите корректный курс.")
        return

    data = await state.get_data()
    currency_name = data.get("currency_name")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post("http://localhost:5001/update_currency", json={"currency_name": currency_name, "rate": rate}) as resp:
                if resp.status == 200:
                    await message.answer(f"Курс валюты {currency_name.upper()} обновлён.")
                elif resp.status == 404:
                    await message.answer("Валюта не найдена.")
                else:
                    await message.answer(f"Ошибка при обновлении: {resp.status}")
        except Exception as e:
            await message.answer(f"Ошибка соединения с currency-manager: {e}")
    await state.clear()


# Установка меню команд с проверкой роли
async def set_commands():
    admin_commands = [
        BotCommand(command="start", description="Начать работу"),
        BotCommand(command="manage_currency", description="Управление валютами"),
        BotCommand(command="get_currencies", description="Показать список валют"),
        BotCommand(command="convert", description="Конвертировать сумму")
    ]

    user_commands = [
        BotCommand(command="start", description="Начать работу"),
        BotCommand(command="get_currencies", description="Показать список валют"),
        BotCommand(command="convert", description="Конвертировать сумму")
    ]

    # Проверка для известных пользователей (например, вручную)
    async with aiohttp.ClientSession() as session:
        known_ids = [1291190562]  # сюда можно добавить других пользователей
        for user_id in known_ids:
            try:
                async with session.get(f"http://localhost:5003/is_admin/{user_id}") as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        if result.get("is_admin"):
                            await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=user_id))
                        else:
                            await bot.set_my_commands(user_commands, scope=BotCommandScopeChat(chat_id=user_id))
            except:
                continue

    await bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())

async def main():
    await set_commands()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

