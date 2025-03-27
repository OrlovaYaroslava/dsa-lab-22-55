#1) Создать обработчик для команды /save_currency. Обработчик
#должен сохранять курс валюты к рублю по следующему алгоритму:
#a. После ввода команды /save_currency бот предлагает ввести название валюты
#b. Пользователь вводит название валюты
#c. После ввода названия валюты бот предлагает ввести курс валюты к рублю
#d. Пользователь вводит курс валюты к рублю
#e. Программа сохраняет название валюты и ее курс в словарь.

import logging
import asyncio
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv


load_dotenv()  # Загружает переменные из .env
API_TOKEN = os.getenv("API_TOKEN")


# Настройка логгера: отображает информацию о работе бота
logging.basicConfig(level=logging.INFO)

# Создание экземпляров бота и диспетчера с памятью для FSM
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Словарь для хранения курсов валют, введённых пользователями
currency_rates = {}


# Определение состояний конечного автомата (FSM)
class CurrencyForm(StatesGroup):
    name = State()  # Состояние ожидания названия валюты
    rate = State()  # Состояние ожидания курса валюты к рублю


# Обработчик команды /start — приветственное сообщение
@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я бот для конвертирования курса валют. "
        "Используй команду /save_currency, чтобы  сохранять курс валюты к рублю. "
        "Используй команду /convert, чтобы  конвертировать указанную валюту в рубль."
    )


# Обработчик команды /save_currency — запуск диалога
@dp.message(Command("save_currency"))
async def cmd_save_currency(message: Message, state: FSMContext) -> None:
    # Запрашиваем у пользователя название валюты
    await message.answer("Введите название валюты:")
    await state.set_state(CurrencyForm.name)


# Обработка ввода названия валюты
@dp.message(CurrencyForm.name)
async def process_currency_name(message: Message, state: FSMContext) -> None:
    # Сохраняем введённое название валюты
    await state.update_data(currency_name=message.text)
    # Переходим к следующему шагу — запрос курса
    await message.answer("Теперь введите курс этой валюты к рублю:")
    await state.set_state(CurrencyForm.rate)


# Обработка ввода курса валюты
@dp.message(CurrencyForm.rate)
async def process_currency_rate(message: Message, state: FSMContext) -> None:
    # Пробуем преобразовать ввод в число
    try:
        rate = float(message.text.replace(',', '.'))
    except ValueError:
        await message.answer("Ошибка: введите число, например 89.5")
        return

    # Получаем ранее сохранённое название валюты
    data = await state.get_data()
    name = data.get("currency_name")

    # Сохраняем валюту и её курс в словарь
    currency_rates[name.lower()] = rate

    # Подтверждаем сохранение пользователю
    await message.answer(f"Сохранено: 1 {name.upper()} = {rate} RUB")

    # Сбрасываем состояние после завершения диалога
    await state.clear()


# Основная асинхронная функция запуска бота
async def main() -> None:
    # Запускаем цикл обработки входящих сообщений
    await dp.start_polling(bot)


#Создать обработчик для команды /convert. Обработчик должен
#конвертировать указанную валюту в рубль по следующему
#алгоритму:
#a. После ввода команды /convert бот предлагает ввести название
#валюты
#b. Пользователь вводит название валюты
#c. После ввода названия валюты бот предлагает ввести сумму в
#указанной валюте
#d. Пользователь вводит число
#e. Бот конвертирует указанную пользователем сумму в рубли по
#ранее сохраненному курсу выбранной валюты


# --- Состояния для команды /convert ---
class ConvertForm(StatesGroup):
    currency = State()  # Состояние ожидания названия валюты
    amount = State()    # Состояние ожидания суммы для конвертации


# Обработчик команды /convert — запуск диалога
@dp.message(Command("convert"))
async def cmd_convert(message: Message, state: FSMContext) -> None:
    # Запрашиваем у пользователя название валюты
    await message.answer("Введите название валюты, которую хотите конвертировать:")
    await state.set_state(ConvertForm.currency)


# Обработка ввода названия валюты
@dp.message(ConvertForm.currency)
async def process_convert_currency(message: Message, state: FSMContext) -> None:
    currency = message.text.lower()

    # Проверяем, есть ли такой курс в словаре
    if currency not in currency_rates:
        await message.answer(
            f"Ошибка: курс для валюты '{currency}' не найден.\n"
            f"Сначала добавьте его через /save_currency."
        )
        await state.clear()
        return

    # Сохраняем валюту и переходим к следующему шагу
    await state.update_data(currency_name=currency)
    await message.answer(f"Введите сумму в {currency.upper()}, которую нужно конвертировать:")
    await state.set_state(ConvertForm.amount)


# Обработка ввода суммы и вывод результата
@dp.message(ConvertForm.amount)
async def process_convert_amount(message: Message, state: FSMContext) -> None:
    try:
        amount = float(message.text.replace(',', '.'))
    except ValueError:
        await message.answer("Ошибка: введите корректное число, например 100.5")
        return

    # Получаем сохранённые данные: название валюты
    data = await state.get_data()
    currency = data.get("currency_name")
    rate = currency_rates.get(currency)

    # Выполняем конвертацию
    result = amount * rate

    # Отправляем результат пользователю
    await message.answer(
        f"{amount} {currency.upper()} = {result:.2f} RUB "
        f"(по курсу 1 {currency.upper()} = {rate} RUB)"
    )

    # Сбрасываем состояние после завершения
    await state.clear()


# Точка входа в программу
if __name__ == "__main__":
    asyncio.run(main())
