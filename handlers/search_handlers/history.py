from telebot.types import Message
from loader import bot


@bot.message_handler(commands=['history'])
def bot_history(message: Message):
    bot.reply_to(message, "История поиска отелей")
