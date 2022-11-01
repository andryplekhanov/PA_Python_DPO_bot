from telebot.types import Message
from loader import bot


@bot.message_handler(content_types=['text'])  # Это было в ТЗ
def get_user_answer(message: Message):
    if message.text.lower() == 'привет':
        bot.reply_to(message, f"Ну, привет, {message.from_user.full_name}!")
