import os
import logging
import asyncio
import pandas as pd

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import load_dotenv

from database import init_db, save_to_db, get_all_sites
from file_processor import process_excel_file,  clean_price
from parser import start_parser_generic
from list_of_parsers import PARSERS

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()

class UploadStates(StatesGroup):
    waiting_for_file = State()

def get_main_kb():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Загрузить файл"))
    return builder.as_markup(resize_keyboard=True)

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бот для сбора данных о зюзюбликах.",
        reply_markup=get_main_kb()
    )

@dp.message(F.text == "Загрузить файл")
async def upload_file(message: types.Message, state: FSMContext):
    await message.answer(
        "Пожалуйста, загрузите Excel-файл со следующими колонками:\n"
        "- title: название сайта\n"
        "- url: ссылка на сайт\n"
        "- xpath: путь к элементу с ценой"
    )
    await state.set_state(UploadStates.waiting_for_file)

@dp.message(UploadStates.waiting_for_file, F.document)
async def handle_document(message: types.Message, state: FSMContext, bot: Bot):
    if not message.document.file_name.endswith(('.xlsx', '.xls')):
        await message.answer("Пожалуйста, загрузите файл в формате Excel")
        return

    try:
        file_path = f"uploads/{message.from_user.id}_{message.document.file_name}"
        file = await bot.get_file(message.document.file_id)
        await bot.download_file(file.file_path, destination=file_path)

        try:
            df = pd.read_excel(file_path)
            missing_cols = set(["title", "url", "xpath"]) - set(df.columns)
            if missing_cols:
                await message.answer(f"В файле отсутствуют обязательные колонки: {missing_cols}.")
                return
        except Exception as e:
            await message.answer(f"Произошла ошибка при чтении файла: {e}")
            return

        df = process_excel_file(file_path)
        save_to_db(df)
        await message.answer("Данные успешно сохранены")
        
        for _, row in df.iterrows():
            site_info = (f"{row['title']}\n"
                        f"Ссылка: {row['url']}\n"
                        f"XPath: {row['xpath']}")
            await message.answer(site_info)
        
        await message.answer("Начинаю парсинг цен...")

        results = {}
        for _, row in df.iterrows():
            try:
                parser = PARSERS.get(row['title'].lower(), start_parser_generic)
                if parser:
                    price = await parser(row['url'], row['xpath'])
                    if price:
                        cleaned_price = clean_price(price)
                        results[row['title']] = int(cleaned_price)
                        
                       
            except Exception as e:
                await message.answer(f"❌ Ошибка парсинга {row['title']}: {str(e)}")
        if results:
            avg_price = sum(results.values()) / len(results)
            await message.answer(f"📊 *Средняя цена:* `{avg_price:.2f} ₽`", parse_mode="Markdown")
        else:
            await message.answer("Не удалось получить ни одной цены.")
    
    except Exception as e:
        logging.error(f"Error: {e}")
        await message.answer(f"Ошибка: {e}")
    
    await state.clear()

async def main():
    init_db()
    os.makedirs("uploads", exist_ok=True)
    
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
