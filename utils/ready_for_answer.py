from loader import bot
from typing import Dict
from telebot.types import Message
from utils.get_hotels import parse_hotels, process_hotels_info, get_hotel_info_str
from utils.get_photos import parse_photos, process_photos


def low_high_price_answer(message: Message, data: Dict) -> None:
    amount_nights = int((data['end_date'] - data['start_date']).total_seconds() / 86400)
    sort_order = 'дешёвых' if data.get('last_command') == 'lowprice' else 'дорогих'
    reply_str = f"✅ Ок, ищем: <b>топ {data['amount_hotels']}</b> " \
                f"самых {sort_order} отелей в городе <b>{data['city']}</b>\n" \
                f"{f'Нужно загрузить фото' if data['need_photo'] else f'Фото не нужны'}" \
                f" — <b>{data['amount_photo']}</b> штук\n" \
                f"Длительность поездки: <b>{amount_nights} ноч.</b> " \
                f"(с {data['start_date']} по {data['end_date']})."
    bot.send_message(message.chat.id, reply_str, parse_mode="html")

    hotels = parse_hotels(data)
    if hotels:
        result_dict = process_hotels_info(hotels.get('results'), amount_nights)
        if result_dict:
            for hotel_id, hotel_data in result_dict.items():
                hotel_info_str = get_hotel_info_str(hotel_data, amount_nights)
                bot.send_message(message.chat.id, hotel_info_str, parse_mode="html", disable_web_page_preview=True)

                if data['need_photo']:
                    print_photo(message, hotel_id, data['amount_photo'])
        else:
            bot.send_message(message.chat.id, '⚠️ Не удалось загрузить информацию по отелям города!')
    else:
        bot.send_message(message.chat.id, '⚠️ Ошибка. Попробуйте ещё раз!')
    return


def print_photo(message: Message, hotel_id: int, amount_photo: int) -> None:
    all_photos = "https://www.hotels.com/ho{id}/?pwaThumbnailDialog=thumbnail-gallery".format(id=hotel_id)
    msg = "<b>🖼 Фото отеля:</b>\n" \
          "    больше фото <a href='{all_photos}'>по ссылке >></a>".format(all_photos=all_photos)
    bot.send_message(message.chat.id, msg, parse_mode="html", disable_web_page_preview=True)

    photos_info_list = parse_photos(hotel_id)
    if photos_info_list:
        photos_list = process_photos(photos_info_list, amount_photo)
        if photos_list:
            for photo_url in photos_list:
                bot.send_photo(message.chat.id, photo_url)
        else:
            bot.send_message(message.chat.id, '⚠️ Ошибка загрузки фото.')
    else:
        bot.send_message(message.chat.id, '⚠️ Ошибка загрузки фото.')


def best_deal_answer(message: Message, data: Dict) -> None:
    amount_nights = int((data['end_date'] - data['start_date']).total_seconds() / 86400)
    reply_str = f"✅ Ок, ищем: <b>топ {data['amount_hotels']}</b> отелей в городе <b>{data['city']}</b>\n" \
                f"В ценовом диапазоне <b>от {data['start_price']}$ до {data['end_price']}$</b>\n" \
                f"Максимальная удаленность от центра: <b>{data['end_distance']} Км</b>\n" \
                f"{f'Нужно загрузить фото' if data['need_photo'] else f'Фото не нужны'}" \
                f" — <b>{data['amount_photo']}</b> штук\n" \
                f"Длительность поездки: <b>{amount_nights} ноч.</b> " \
                f"(с {data['start_date']} по {data['end_date']})."
    bot.send_message(message.chat.id, reply_str, parse_mode="html")

    hotels = parse_hotels(data)
    if hotels:
        result_dict = process_hotels_info(hotels.get('results'), amount_nights)
        if result_dict:
            hotels_counter = 0
            for hotel_id, hotel_data in result_dict.items():
                if hotels_counter >= data.get('amount_hotels'):
                    break
                current_distance = hotel_data.get('distance_city_center')
                if not current_distance:
                    continue
                if current_distance <= data.get('end_distance'):
                    hotel_info_str = get_hotel_info_str(hotel_data, amount_nights)
                    bot.send_message(message.chat.id, hotel_info_str, parse_mode="html", disable_web_page_preview=True)

                    if data['need_photo']:
                        print_photo(message, hotel_id, data['amount_photo'])
                    hotels_counter += 1
            if hotels_counter == 0:
                bot.send_message(message.chat.id, '⚠️ Ничего не нашлось! Измените критерии поиска!')
        else:
            bot.send_message(message.chat.id, '⚠️ По вашему запрос ничего не нашлось! Измените критерии поиска!')
    else:
        bot.send_message(message.chat.id, '⚠️ Ошибка. Ничего не нашлось!')
