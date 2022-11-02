from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def get_yes_no() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(True, True)
    keyboard.add(
        KeyboardButton(text='Да'),
        KeyboardButton(text='Нет')
    )
    return keyboard
