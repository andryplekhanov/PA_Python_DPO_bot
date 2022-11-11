from telebot.types import Message
from loader import bot
from database.db_controller import save_user


@bot.message_handler(commands=['start'])
def bot_start(message: Message) -> None:
    save_user(message)
    bot.delete_state(message.from_user.id, message.chat.id)
    bot.send_message(message.chat.id, f"👋 Привет, {message.from_user.full_name}!\n"
                                      f"Можете ввести какую-нибудь команду!\n"
                                      f"Например: <b>/help</b>", parse_mode="html")
