from telebot.handler_backends import State, StatesGroup


class LowPriceStates(StatesGroup):
    city = State()
    city_id = State()
    cities = State()
    amount_hotels = State()
    need_photo = State()
    amount_photo = State()
    start_date = State()
    end_date = State()
