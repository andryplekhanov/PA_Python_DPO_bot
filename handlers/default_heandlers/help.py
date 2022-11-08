from telebot.types import Message
from config_data.config import DEFAULT_COMMANDS
from loader import bot
from states.search_info import UsersStates


@bot.message_handler(commands=['help'])
def bot_help(message: Message):
    bot.delete_state(message.from_user.id, message.chat.id)
    text = [f'<b>/{command}</b> - {desk}' for command, desk in DEFAULT_COMMANDS]
    bot.reply_to(message, '\n'.join(text), parse_mode='html')


@bot.message_handler(state=UsersStates.last_command)
def bot_a_help(message: Message):
    bot.delete_state(message.from_user.id, message.chat.id)
    text = [f'<b>/{command}</b> - {desk}' for command, desk in DEFAULT_COMMANDS]
    bot.send_message(message.from_user.id, '\n'.join(text), parse_mode='html')
