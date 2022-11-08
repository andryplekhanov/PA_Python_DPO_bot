from loader import bot
from typing import Dict
from telebot.types import Message
from utils.get_hotels import parse_hotels, process_hotels_info, get_hotel_info_str
from utils.get_photos import parse_photos, process_photos


def ready_for_answer(message: Message, data: Dict) -> None:
    amount_nights = int((data['end_date'] - data['start_date']).total_seconds() / 86400)
    sort_order = 'дешёвых' if data.get('last_command') == 'lowprice' else 'дорогих'
    reply_str = f"✅ Ок, ищем: <b>топ {data['amount_hotels']}</b> " \
                f"самых {sort_order} отелей в городе <b>{data['city']}</b>\n" \
                f"{f'Нужно загрузить фото' if data['need_photo'] else f'Фото не нужны'}" \
                f" — <b>{data['amount_photo']}</b> штук\n" \
                f"Длительность поездки: <b>{amount_nights} ноч.</b> " \
                f"(с {data['start_date']} по {data['end_date']})."
    bot.edit_message_text(reply_str, message.chat.id, message.message_id, parse_mode="html")

    hotels = parse_hotels(data).get('results')
    if hotels:
        result_dict = process_hotels_info(hotels, amount_nights)
        if result_dict:
            for hotel_id, hotel_data in result_dict.items():
                hotel_info_str = get_hotel_info_str(hotel_data, amount_nights)
                bot.send_message(message.chat.id, hotel_info_str, parse_mode="html", disable_web_page_preview=True)

                if data['need_photo']:
                    all_photos = "https://www.hotels.com/ho{id}/?pwaThumbnailDialog=thumbnail-gallery".format(
                        id=hotel_id)
                    msg = "<b>🖼 Фото отеля:</b>\n" \
                          "    больше фото <a href='{all_photos}'>по ссылке >></a>".format(all_photos=all_photos)
                    bot.send_message(message.chat.id, msg, parse_mode="html", disable_web_page_preview=True)

                    photos_info_list = parse_photos(hotel_id)
                    if photos_info_list:
                        photos_list = process_photos(photos_info_list, data['amount_photo'])
                        if photos_list:
                            for photo_url in photos_list:
                                bot.send_photo(message.chat.id, photo_url)
                        else:
                            bot.send_message(message.chat.id, '⚠️ Ошибка загрузки фото.')
                    else:
                        bot.send_message(message.chat.id, '⚠️ Ошибка загрузки фото.')
        else:
            bot.send_message(message.chat.id, '⚠️ Не удалось загрузить информацию по отелям города!')
    else:
        bot.send_message(message.chat.id, '⚠️ Ошибка. Попробуйте ещё раз!')
    return
