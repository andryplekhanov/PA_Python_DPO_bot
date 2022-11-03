from telebot.types import Message
from keyboards.reply.yes_no_reply import get_yes_no
from keyboards.inline.calendar import print_calendar
from datetime import date, timedelta
from loader import bot
from states.search_info import LowPriceStates
from telegram_bot_calendar import DetailedTelegramCalendar


@bot.message_handler(commands=['lowprice'])
def bot_lowprice(message: Message):
    bot.set_state(message.from_user.id, LowPriceStates.city, message.chat.id)
    bot.send_message(message.from_user.id, 'Введите город')


@bot.message_handler(state=LowPriceStates.city, is_digit=False)  # Если название города - не цифры
def get_city(message: Message):
    bot.send_message(message.from_user.id, 'Сколько отелей найти?')
    bot.set_state(message.from_user.id, LowPriceStates.amount_hotels, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['city'] = message.text.lower()


@bot.message_handler(state=LowPriceStates.city, is_digit=True)  # Если название города - цифры
def get_city(message: Message):
    bot.send_message(message.from_user.id, 'Название города должно состоять из букв')


@bot.message_handler(state=LowPriceStates.amount_hotels, is_digit=True)  # Если количество отелей - число
def get_amount_hotels(message: Message):
    if 1 <= int(message.text) <= 10:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['amount_hotels'] = int(message.text)
        bot.set_state(message.from_user.id, LowPriceStates.need_photo, message.chat.id)
        bot.send_message(message.from_user.id, 'Желаете загрузить фото отелей?', reply_markup=get_yes_no())
    else:
        bot.send_message(message.from_user.id, 'Количество отелей в топе должно быть от 1 до 10')


@bot.message_handler(state=LowPriceStates.amount_hotels, is_digit=False)  # Если количество отелей - не число
def amount_hotels_incorrect(message: Message):
    bot.send_message(message.from_user.id, 'Введите число от 1 до 10')


@bot.message_handler(state=LowPriceStates.need_photo)
def get_need_photo(message: Message):
    if message.text == 'Да':
        bot.send_message(message.from_user.id, text='Введите количество фото')
        bot.set_state(message.from_user.id, LowPriceStates.amount_photo, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['need_photo'] = True
    elif message.text == 'Нет':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['need_photo'] = False
            data['amount_photo'] = 0
        ask_for_start_date(message)
    else:
        bot.send_message(message.from_user.id, text='Напишите "Да" или "Нет"')


@bot.message_handler(state=LowPriceStates.amount_photo, is_digit=True)  # Если количество фото - число
def get_amount_photo(message: Message):
    if 1 <= int(message.text) <= 10:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['amount_photo'] = int(message.text)
        ask_for_start_date(message)
    else:
        bot.send_message(message.from_user.id, 'Количество фото должно быть от 1 до 10')


@bot.message_handler(state=LowPriceStates.amount_photo, is_digit=False)  # Если количество фото - не число
def amount_photo_incorrect(message: Message):
    bot.send_message(message.from_user.id, 'Введите число от 1 до 10')


def ask_for_start_date(message: Message):
    calendar, step = DetailedTelegramCalendar(min_date=date.today()).build()
    bot.send_message(message.chat.id, f"Введите дату заезда", reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def date_reply(call):
    with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data:
        if not data.get('start_date'):
            result, key, step = DetailedTelegramCalendar(min_date=date.today()).process(call.data)
        elif not data.get('end_date'):
            result, key, step = DetailedTelegramCalendar(min_date=data.get('start_date') + timedelta(1)).process(call.data)

    if not result and key:
        bot.edit_message_text(f"Введите дату", call.message.chat.id,
                              call.message.message_id, reply_markup=key)
    elif result:
        with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data:
            if not data.get('start_date'):
                data['start_date'] = result
                ask_for_end_date(call.message, result)
            elif not data.get('end_date'):
                data['end_date'] = result
                data_dict = data
                bot.delete_state(call.message.from_user.id, call.message.chat.id)
                ready_for_answer(call.message, data_dict)


def ask_for_end_date(message, start_date):
    calendar, step = DetailedTelegramCalendar(min_date=start_date + timedelta(1)).build()
    bot.send_message(message.chat.id, f"Введите дату выезда", reply_markup=calendar)


def ready_for_answer(message, data):
    amount_nights = int((data['end_date'] - data['start_date']).total_seconds() / 86400)
    reply_str = f"Ок, ищем: <b>топ {data['amount_hotels']}</b> " \
                f"самых дешёвых отелей в городе <b>{data['city'].capitalize()}</b>\n" \
                f"{f'Нужно загрузить фото' if data['need_photo'] else f'Фото не нужны'}" \
                f" — <b>{data['amount_photo']}</b> штук\n" \
                f"Длительность поездки: <b>{amount_nights} ноч.</b> " \
                f"(с {data['start_date']} по {data['end_date']})."
    bot.send_message(message.chat.id, reply_str, parse_mode="html")

    # querystring = {"q": "new york", "locale": "en_US", "langid": "1033", "siteid": "300000001"}
    # response = requests.request("GET", config.RAPID_API_URL, headers=config.RAPID_API_HEADERS, params=querystring)
