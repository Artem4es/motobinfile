import os

from dotenv import load_dotenv

from telegram import Bot

load_dotenv()
TELEGRAM_TOKEN: str = os.environ['TELEGRAM_TOKEN']
ADMIN_ID: int = os.environ['ADMIN_ID']

bot: str = Bot(token=TELEGRAM_TOKEN)


def send_message(message: str) -> None:
    bot.send_message(chat_id=ADMIN_ID, text=message)
