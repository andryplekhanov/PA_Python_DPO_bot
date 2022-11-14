from telebot.types import Message
from states.search_info import UsersStates
from loader import bot


@bot.message_handler(content_types=['text'])  # Это было в ТЗ
def get_user_answer(message: Message):
    """
    Функция, реагирующая на ввод пользователем сообщения 'привет'.

    :param message: сообщение Telegram
    """

    bot.delete_state(message.from_user.id, message.chat.id)
    bot.set_state(message.from_user.id, UsersStates.last_command, message.chat.id)
    if message.text.lower() == 'привет':
        bot.reply_to(message, f"Ну, привет, {message.from_user.full_name}! Введи команду /help")
