from loader import bot
from telebot.types import Message, CallbackQuery
from keyboards.inline.yes_no_reply import get_yes_no
from keyboards.inline.cities_for_choice import print_cities
from keyboards.inline.cities_for_choice import for_city
from states.search_info import LowPriceStates
from telegram_bot_calendar import DetailedTelegramCalendar
from datetime import date, timedelta
from utils.get_cities import parse_cities_group
import re


@bot.message_handler(commands=['lowprice'])
def bot_low_price(message: Message):
    bot.set_state(message.from_user.id, LowPriceStates.cities, message.chat.id)
    bot.send_message(message.from_user.id, 'Введите город')


@bot.message_handler(state=LowPriceStates.cities, is_digit=True)  # Если название города - цифры
def get_city_incorrect(message: Message):
    bot.send_message(message.from_user.id, 'Название города должно состоять из букв')


@bot.message_handler(state=LowPriceStates.cities, is_digit=False)  # Если название города - не цифры
def get_city(message: Message):
    cities_dict = parse_cities_group(message.text)
    if cities_dict:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['cities'] = cities_dict
        bot.send_message(message.from_user.id, 'Пожалуйста, уточните:', reply_markup=print_cities(cities_dict))
    else:
        bot.send_message(message.from_user.id, 'Не нахожу такой город. Введите ещё раз.')


@bot.callback_query_handler(func=None, city_config=for_city.filter())
def clarify_city(call: CallbackQuery):
    with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data:
        data['city_id'] = re.search(r'\d+', call.data).group()
        data['city'] = [city for city, city_id in data['cities'].items() if city_id == data['city_id']][0]
    bot.set_state(call.from_user.id, LowPriceStates.amount_hotels, call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Сколько отелей найти?')


@bot.message_handler(state=LowPriceStates.amount_hotels, is_digit=True)  # Если количество отелей - число
def get_amount_hotels(message: Message):
    if 1 <= int(message.text) <= 10:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['amount_hotels'] = int(message.text)
        bot.send_message(message.from_user.id, 'Желаете загрузить фото отелей?', reply_markup=get_yes_no())
    else:
        bot.send_message(message.from_user.id, 'Количество отелей в топе должно быть от 1 до 10')


@bot.message_handler(state=LowPriceStates.amount_hotels, is_digit=False)  # Если количество отелей - не число
def amount_hotels_incorrect(message: Message):
    bot.send_message(message.from_user.id, 'Количество отелей должно быть от 1 до 10')


@bot.callback_query_handler(func=lambda call: call.data == 'yes' or call.data == 'no')
def need_photo_reply(call):
    with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data:
        if call.data == "yes":
            bot.send_message(call.message.chat.id, text='Введите количество фото')
            data['need_photo'] = True
            bot.set_state(call.from_user.id, LowPriceStates.amount_photo, call.message.chat.id)
        elif call.data == "no":
            data['need_photo'] = False
            data['amount_photo'] = 0
            calendar, step = DetailedTelegramCalendar(min_date=date.today()).build()
            bot.send_message(call.message.chat.id, f"Введите дату заезда", reply_markup=calendar)
        else:
            bot.send_message(call.message.chat.id, text='Нажмите кнопку "Да" или "Нет"')


@bot.message_handler(state=LowPriceStates.amount_photo, is_digit=True)  # Если количество фото - число
def get_amount_photo(message: Message):
    if 1 <= int(message.text) <= 10:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['amount_photo'] = int(message.text)
        calendar, step = DetailedTelegramCalendar(min_date=date.today()).build()
        bot.send_message(message.chat.id, f"Введите дату заезда", reply_markup=calendar)
    else:
        bot.send_message(message.from_user.id, 'Количество фото должно быть от 1 до 10')


@bot.message_handler(state=LowPriceStates.amount_photo, is_digit=False)  # Если количество фото - не число
def amount_photo_incorrect(message: Message):
    bot.send_message(message.from_user.id, 'Количество фото от 1 до 10')


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def date_reply(call):
    with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data:
        if not data.get('start_date'):
            result, key, step = DetailedTelegramCalendar(min_date=date.today()).process(call.data)
        elif not data.get('end_date'):
            new_start_date = data.get('start_date') + timedelta(1)
            result, key, step = DetailedTelegramCalendar(min_date=new_start_date).process(call.data)

    if not result and key:
        bot.edit_message_text(f"Введите дату", call.message.chat.id,
                              call.message.message_id, reply_markup=key)
    elif result:
        with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data:
            if not data.get('start_date'):
                data['start_date'] = result
                calendar, step = DetailedTelegramCalendar(min_date=result + timedelta(1)).build()
                bot.send_message(call.message.chat.id, f"Введите дату выезда", reply_markup=calendar)
            elif not data.get('end_date'):
                data['end_date'] = result
                data_dict = data
                ready_for_answer(call.message, data_dict)


def ready_for_answer(message, data):
    bot.delete_state(message.from_user.id, message.chat.id)
    amount_nights = int((data['end_date'] - data['start_date']).total_seconds() / 86400)
    reply_str = f"Ок, ищем: <b>топ {data['amount_hotels']}</b> " \
                f"самых дешёвых отелей в городе <b>{data['city']}</b>\n" \
                f"{f'Нужно загрузить фото' if data['need_photo'] else f'Фото не нужны'}" \
                f" — <b>{data['amount_photo']}</b> штук\n" \
                f"Длительность поездки: <b>{amount_nights} ноч.</b> " \
                f"(с {data['start_date']} по {data['end_date']})."
    bot.send_message(message.chat.id, reply_str, parse_mode="html")
