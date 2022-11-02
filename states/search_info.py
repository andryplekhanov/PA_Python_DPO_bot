from telebot.handler_backends import State, StatesGroup


class UserSearchState(StatesGroup):
    city = State()
    amount_hotels = State()
    need_photo = State()
    amount_photo = State()
    price_range = State()
    distance_from = State()
    distance_to = State()
