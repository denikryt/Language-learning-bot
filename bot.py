from telebot import TeleBot
from dotenv import load_dotenv
import os

load_dotenv()
BOT = TeleBot(os.getenv('BOT_TOKEN'), threaded=False)