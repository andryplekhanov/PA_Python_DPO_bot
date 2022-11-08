from telebot.types import Message
from loader import bot


@bot.message_handler(content_types=['text'])  # Это было в ТЗ
def get_user_answer(message: Message):
    bot.delete_state(message.from_user.id, message.chat.id)
    if message.text.lower() == 'привет':
        bot.reply_to(message, f"Ну, привет, {message.from_user.full_name}! Введи команду /help")
