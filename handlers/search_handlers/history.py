from telebot.types import Message, CallbackQuery
from loader import bot
from keyboards.inline.history_action_choice import get_history_action
from utils.get_history import show_history, delete_history


@bot.message_handler(commands=['history'])
def bot_history(message: Message):
    bot.delete_state(message.from_user.id, message.chat.id)
    bot.send_message(message.from_user.id, 'Пожалуйста, уточните:', reply_markup=get_history_action())


@bot.callback_query_handler(func=lambda call: call.data == 'show_history' or call.data == 'delete_history')
def process_history_reply(call: CallbackQuery) -> None:
    if call.data == "show_history":
        bot.send_message(call.message.chat.id, text='История поиска:')
        show_history()
    elif call.data == "delete_history":
        delete_history()
        bot.send_message(call.message.chat.id, text='История поиска очищена!')
    bot.send_message(call.message.chat.id,
                     f"😉👌 Вот как-то так.\nМожете ввести ещё какую-нибудь команду!\n"
                     f"Например: <b>/help</b>", parse_mode="html")
