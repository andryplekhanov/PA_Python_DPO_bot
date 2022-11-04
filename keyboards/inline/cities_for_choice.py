from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.callback_data import CallbackData

for_city = CallbackData('city_id', prefix="search")


def print_cities(cities_dict) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)

    for city, city_id in cities_dict.items():
        keyboard.add(InlineKeyboardButton(text=city, callback_data=for_city.new(city_id=city_id)))
    return keyboard
