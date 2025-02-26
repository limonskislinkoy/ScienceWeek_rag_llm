import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
from dotenv import load_dotenv
import os

import load_balancer


class TelegramBot:
    def __init__(self, token: str, load_balancer: load_balancer.LoadBalancer):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.keyboard_inline_menu = self.create_keyboard_inline_menu()
        self.keyboard_menu = self.create_keyboard_menu()
        self.register_handlers()

        self.load_balancer = load_balancer
        self.ready_to_download_file = False

    def create_keyboard_inline_menu(self):
        keyboard = InlineKeyboardBuilder()
        keyboard.row(InlineKeyboardButton(text="Меню", callback_data="open_menu"))
        return keyboard

    def create_keyboard_menu(self):
        layout = [
            [
                types.KeyboardButton(text="/add"),
            ]
        ]
        keyboard = ReplyKeyboardMarkup(keyboard=layout, resize_keyboard=True)
        return keyboard

    def register_handlers(self):
        self.dp.message(CommandStart())(self.start_handler)
        self.dp.message(Command("add"))(self.request_to_upload_file)
        self.dp.message(F.text)(self.message_handler)
        self.dp.message(F.document)(self.file_handler)
        self.dp.callback_query()(self.callback_handler)

    async def start_handler(self, message: types.Message):
        await message.answer(
            "Здравствуйте! Я бот-ассистент, чем могу помочь?",
            reply_markup=self.keyboard_inline_menu.as_markup(),
        )

    async def callback_handler(self, callback: types.CallbackQuery):
        if callback.data == "open_menu":
            await callback.message.answer(
                text="Выберите действие:", reply_markup=self.keyboard_menu
            )
        await callback.answer()

    async def message_handler(self, message: types.Message):
        request = str(message.text)
        answer = self.load_balancer.test_request(request)
        await message.answer(f"{answer}")

    async def request_to_upload_file(self, message: types.Message):
        self.ready_to_download_file = True
        await message.answer("Я готов принимать файл, как будете готовы - отправляйте:")

    async def file_handler(self, message: types.Message, bot: Bot):
        if self.ready_to_download_file:
            main_directory = os.path.dirname(__file__)
            relative_dir = "\\documents\\"
            file_path = f"{main_directory+relative_dir+message.document.file_id}.txt"
            await bot.download(
                message.document,
                destination=file_path,
            )
            self.load_balancer.test_load_file(file_path=file_path)
            await message.answer("Файл успешно принят, спасибо!")
        else:
            await message.answer("Нет доступа для добавления файлов")

    async def run(self):
        await self.dp.start_polling(self.bot)


def initialize_and_run(load_balancer: load_balancer.LoadBalancer) -> TelegramBot:
    # Включаем логирование
    logging.basicConfig(level=logging.INFO)
    load_dotenv()
    bot_instance = TelegramBot(
        token=str(os.getenv("TELEGRAM_BOT_API")), load_balancer=load_balancer
    )
    asyncio.run(bot_instance.run())
    return bot_instance
