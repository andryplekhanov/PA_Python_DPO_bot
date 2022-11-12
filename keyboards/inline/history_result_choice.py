from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.factories import for_history
from typing import List
from datetime import datetime


def print_histories(histories_list: List) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    for history in histories_list:
        text = f'{datetime.fromtimestamp(history.date).strftime("%d.%m.%Y, %H:%M")} — ' \
               f'{history.command} — {history.city}'
        keyboard.add(InlineKeyboardButton(text=text, callback_data=for_history.new(history_id=history.id)))
    return keyboard
