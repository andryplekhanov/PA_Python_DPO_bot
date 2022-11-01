from telebot.types import Message
from loader import bot


@bot.message_handler(commands=['hello-world'])  # Это было в ТЗ
def hello_world(message: Message):
    bot.reply_to(message, f"Вы ввели 'hello-world'!")
