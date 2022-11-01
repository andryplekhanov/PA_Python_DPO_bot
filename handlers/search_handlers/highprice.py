from telebot.types import Message
from loader import bot


@bot.message_handler(commands=['highprice'])
def bot_highprice(message: Message):
    bot.reply_to(message, "Топ самых дорогих отелей в городе")
