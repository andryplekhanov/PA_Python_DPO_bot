from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.factories import for_city
from typing import Dict


def print_cities(cities_dict: Dict[str, str]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)

    for city, city_id in cities_dict.items():
        keyboard.add(InlineKeyboardButton(text=city, callback_data=for_city.new(city_id=city_id)))
    return keyboard
