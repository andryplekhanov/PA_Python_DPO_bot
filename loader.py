from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data import config
from peewee import SqliteDatabase

storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)
db = SqliteDatabase('search_history.db')
