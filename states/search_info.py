from telebot.handler_backends import State, StatesGroup


class UsersStates(StatesGroup):
    last_command = State()
    city = State()
    city_id = State()
    cities = State()
    amount_hotels = State()
    need_photo = State()
    amount_photo = State()
    start_date = State()
    end_date = State()
    start_price = State()
    end_price = State()
    start_distance = State()
    end_distance = State()
