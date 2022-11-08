from loader import bot
from telebot.types import Message, CallbackQuery
from keyboards.inline.yes_no_reply import get_yes_no
from keyboards.inline.cities_for_choice import print_cities
from utils.factories import for_city
from states.search_info import UsersStates
from telegram_bot_calendar import DetailedTelegramCalendar
from datetime import date, timedelta
from utils.get_cities import parse_cities_group
from utils.ready_for_answer import low_high_price_answer, best_deal_answer
import re


@bot.message_handler(state=UsersStates.cities, is_digit=True)  # Если название города - цифры
def get_city_incorrect(message: Message) -> None:
    bot.send_message(message.from_user.id, '⚠️ Название города должно состоять из букв')


@bot.message_handler(state=UsersStates.cities, is_digit=False)  # Если название города - не цифры
def get_city(message: Message) -> None:
    cities_dict = parse_cities_group(message.text)
    if cities_dict:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['cities'] = cities_dict
        bot.send_message(message.from_user.id, 'Пожалуйста, уточните:', reply_markup=print_cities(cities_dict))
    else:
        bot.send_message(message.from_user.id, '⚠️ Не нахожу такой город. Введите ещё раз.')


@bot.callback_query_handler(func=None, city_config=for_city.filter())
def clarify_city(call: CallbackQuery) -> None:
    with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data:
        data['city_id'] = re.search(r'\d+', call.data).group()
        data['city'] = [city for city, city_id in data['cities'].items() if city_id == data['city_id']][0]
    bot.set_state(call.from_user.id, UsersStates.amount_hotels, call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Сколько отелей найти?')


@bot.message_handler(state=UsersStates.amount_hotels, is_digit=True)  # Если количество отелей - число
def get_amount_hotels(message: Message) -> None:
    if 1 <= int(message.text) <= 10:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['amount_hotels'] = int(message.text)
        bot.send_message(message.from_user.id, 'Желаете загрузить фото отелей?', reply_markup=get_yes_no())
    else:
        bot.send_message(message.from_user.id, '⚠️ Количество отелей в топе должно быть от 1 до 10')


@bot.message_handler(state=UsersStates.amount_hotels, is_digit=False)  # Если количество отелей - не число
def amount_hotels_incorrect(message: Message) -> None:
    bot.send_message(message.from_user.id, '⚠️ Количество отелей должно быть от 1 до 10')


@bot.callback_query_handler(func=lambda call: call.data == 'yes' or call.data == 'no')
def need_photo_reply(call: CallbackQuery) -> None:
    with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data:
        if call.data == "yes":
            bot.send_message(call.message.chat.id, text='Введите количество фото')
            data['need_photo'] = True
            bot.set_state(call.from_user.id, UsersStates.amount_photo, call.message.chat.id)
        elif call.data == "no":
            data['need_photo'] = False
            data['amount_photo'] = 0
            calendar, step = DetailedTelegramCalendar(min_date=date.today()).build()
            bot.send_message(call.message.chat.id, f"Введите дату заезда", reply_markup=calendar)
        else:
            bot.send_message(call.message.chat.id, text='⚠️ Нажмите кнопку "Да" или "Нет"')


@bot.message_handler(state=UsersStates.amount_photo, is_digit=True)  # Если количество фото - число
def get_amount_photo(message: Message) -> None:
    if 1 <= int(message.text) <= 10:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['amount_photo'] = int(message.text)
        calendar, step = DetailedTelegramCalendar(min_date=date.today()).build()
        bot.send_message(message.chat.id, f"Введите дату заезда", reply_markup=calendar)
    else:
        bot.send_message(message.from_user.id, '⚠️ Количество фото должно быть от 1 до 10')


@bot.message_handler(state=UsersStates.amount_photo, is_digit=False)  # Если количество фото - не число
def amount_photo_incorrect(message: Message) -> None:
    bot.send_message(message.from_user.id, '⚠️ Количество фото от 1 до 10')


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def date_reply(call: CallbackQuery) -> None:
    with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data:
        if not data.get('start_date'):
            result, key, step = DetailedTelegramCalendar(min_date=date.today()).process(call.data)
        elif not data.get('end_date'):
            new_start_date = data.get('start_date') + timedelta(1)
            result, key, step = DetailedTelegramCalendar(min_date=new_start_date).process(call.data)

    if not result and key:
        bot.edit_message_text("Введите дату", call.message.chat.id, call.message.message_id, reply_markup=key)
    elif result:
        with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data:
            if not data.get('start_date'):
                data['start_date'] = result
                calendar, step = DetailedTelegramCalendar(min_date=result + timedelta(1)).build()
                bot.edit_message_text("Введите дату выезда",
                                      call.message.chat.id, call.message.message_id, reply_markup=calendar)
            elif not data.get('end_date'):
                data['end_date'] = result

                if data.get('last_command') in ('lowprice', 'highprice'):
                    data_dict = data
                    low_high_price_answer(call.message, data_dict)
                    bot.set_state(call.from_user.id, UsersStates.last_command, call.message.chat.id)
                    bot.send_message(call.message.chat.id,
                                     f"👍 Вот как-то так.\nМожете ввести ещё какую-нибудь команду!\n"
                                     f"Например: <b>/help</b>", parse_mode="html")
                else:
                    bot.set_state(call.from_user.id, UsersStates.start_price, call.message.chat.id)
                    bot.send_message(call.message.chat.id, "Введите минимальную цену за ночь $:")


@bot.message_handler(state=UsersStates.start_price, is_digit=True)  # Если количество $ - число
def get_start_price(message: Message) -> None:
    if int(message.text) > 0:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['start_price'] = int(message.text)
        bot.set_state(message.from_user.id, UsersStates.end_price, message.chat.id)
        bot.send_message(message.chat.id, "Введите максимальную цену за ночь $:")
    else:
        bot.send_message(message.from_user.id, '⚠️ Введите число больше нуля')


@bot.message_handler(state=UsersStates.start_price, is_digit=False)  # Если количество $ - не число
def start_price_incorrect(message: Message) -> None:
    bot.send_message(message.from_user.id, '⚠️ Введите число больше нуля')


@bot.message_handler(state=UsersStates.end_price, is_digit=True)  # Если количество $ - число
def get_end_price(message: Message) -> None:
    if int(message.text) > 0:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if int(message.text) > data['start_price']:
                data['end_price'] = int(message.text)
                bot.set_state(message.from_user.id, UsersStates.start_distance, message.chat.id)
                bot.send_message(message.chat.id, "Введите минимальное расстояние до центра в км\n"
                                                  "(например 0.1):")
            else:
                bot.send_message(message.chat.id,
                                 f"⚠️ Максимальная цена должна быть больше {data['start_price']}$")
    else:
        bot.send_message(message.from_user.id, '⚠️ Введите число больше нуля')


@bot.message_handler(state=UsersStates.end_price, is_digit=False)  # Если количество $ - не число
def end_price_incorrect(message: Message) -> None:
    bot.send_message(message.from_user.id, '⚠️ Введите число больше нуля')


@bot.message_handler(state=UsersStates.start_distance)
def get_start_distance(message: Message) -> None:
    if ',' in message.text:
        message.text = message.text.replace(',', '.')

    try:
        message.text = float(message.text)
        if message.text > 0:
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['start_distance'] = message.text
            bot.set_state(message.from_user.id, UsersStates.end_distance, message.chat.id)
            bot.send_message(message.chat.id, "Введите максимальное расстояние до центра в км\n"
                                              "(например 15.5):")
        else:
            bot.send_message(message.from_user.id, '⚠️ Введите число больше нуля')
    except Exception:
        bot.send_message(message.chat.id, "⚠️Введите число - минимальное расстояние до центра в км\n"
                                          "(например 0.1):")


@bot.message_handler(state=UsersStates.end_distance)
def get_end_distance(message: Message) -> None:
    if ',' in message.text:
        message.text = message.text.replace(',', '.')

    try:
        message.text = float(message.text)
        if message.text > 0:
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                if message.text > data['start_distance']:
                    data['end_distance'] = message.text
                    data_dict = data
                    best_deal_answer(message, data_dict)
                    bot.set_state(message.from_user.id, UsersStates.last_command, message.chat.id)
                    bot.send_message(message.chat.id,
                                     f"👍 Вот как-то так.\nМожете ввести ещё какую-нибудь команду!\n"
                                     f"Например: <b>/help</b>", parse_mode="html")
                else:
                    bot.send_message(message.chat.id,
                                     f"⚠️ Максимальное расстояние должно быть больше {data['start_distance']}")
        else:
            bot.send_message(message.from_user.id, '⚠️ Введите число больше нуля')

    except Exception:
        bot.send_message(message.chat.id, "⚠️Введите число - максимальное расстояние до центра в км\n"
                                          "(например 15.5):")
