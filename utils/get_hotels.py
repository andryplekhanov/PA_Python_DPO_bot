from typing import Dict, List, Union
from utils.api_reqiest import request_to_api
from config_data.config import RAPID_API_HEADERS, RAPID_API_ENDPOINTS
from loguru import logger
import re
import json


@logger.catch
def parse_hotels(data_dict: Dict) -> Union[Dict[str, List[Dict]], None]:
    """
    Функция делает запрос в request_to_api и десериализирует результат. Если запрос получен и десериализация прошла -
    возвращает обработанный результат в виде словаря, иначе None.

    :param data_dict: словарь - данные для запроса по api.
    :return: None или словарь с ключом 'results' и значением - списком словарей полученных отелей.
    """

    if data_dict.get('last_command') == 'highprice':
        sort_order = 'PRICE_HIGHEST_FIRST'
    elif data_dict.get('last_command') == 'bestdeal':
        sort_order = 'DISTANCE_FROM_LANDMARK'
    else:
        sort_order = 'PRICE'

    if data_dict.get('last_command') in ('highprice', 'lowprice'):
        querystring = {
            "destinationId": data_dict['city_id'], "pageNumber": "1", "pageSize": data_dict['amount_hotels'],
            "checkIn": data_dict['start_date'], "checkOut": data_dict['end_date'], "adults1": "1",
            "sortOrder": sort_order, "locale": "ru_RU", "currency": "USD"}
    else:
        querystring = {"destinationId": data_dict['city_id'], "pageNumber": "1", "pageSize": 25,
                       "checkIn": data_dict['start_date'], "checkOut": data_dict['end_date'], "adults1": "1",
                       "sortOrder": sort_order, "locale": "ru_RU", "currency": "USD",
                       'priceMin': data_dict['start_price'], 'priceMax': data_dict['end_price'],
                       'landmarkIds': 'Центр города'}

    responce = request_to_api(
        url=RAPID_API_ENDPOINTS['hotel-list'],
        querystring=querystring,
        headers=RAPID_API_HEADERS)
    if responce:
        pattern = r'(?<=,)"results":.+?(?=,"pagination)'
        find = re.search(pattern, responce.text)
        if find:
            result = json.loads(f"{{{find[0]}}}")
            return result
    return None


@logger.catch
def process_hotels_info(hotels_info_list: List[Dict], amount_nights: int) -> Dict[int, Dict]:
    """
    Функция получает список словарей - результат парсинга отелей, выбирает нужную информацию, обрабатывает и складывает
    в словарь hotels_info_dict

    :param hotels_info_list: список со словарями. Каждый словарь - полная информация по отелю (результат парсинга).
    :param amount_nights: количество ночей.
    :return: словарь с информацией по отелю: {hotel_id: {hotel_info}} (теоретически может быть пустым).
    """

    hotels_info_dict = dict()
    for hotel in hotels_info_list:
        hotel_id = hotel.get('id')
        if not hotel_id:
            continue
        hotel_url = f'https://www.hotels.com/ho{str(hotel_id)}/'
        hotel_name = hotel.get('name', 'No name')
        price_per_night = hotel.get('ratePlan', {}).get('price', {}).get('exactCurrent', 0)
        total_price = round(price_per_night * amount_nights, 2)

        distance_city_center = 0.0
        if hotel.get('landmarks'):
            for landmark in hotel.get('landmarks'):
                if landmark.get('label') in ('Центр города', 'City center'):
                    distance = landmark.get('distance').split()[0]
                    if ',' in distance:
                        distance = distance.replace(',', '.')
                    distance_city_center = float(distance)
                    break

        hotel_neighbourhood = hotel.get('neighbourhood', 'No data')

        hotels_info_dict[hotel_id] = {
            'name': hotel_name,
            'price_per_night': price_per_night,
            'total_price': total_price,
            'distance_city_center': distance_city_center,
            'hotel_url': hotel_url,
            'hotel_neighbourhood': hotel_neighbourhood
        }
    return hotels_info_dict


@logger.catch
def get_hotel_info_str(hotel_data: Dict, amount_nights: int) -> str:
    """
    Функция преобразует данные по отелю из словаря в строку с html.
    Используется для вывода информации через сообщение (bot.send_message).

    :param hotel_data: словарь с информацией по отелю.
    :param amount_nights: количество ночей.
    :return: строка с html с информацией по отелю
    """

    result = f"<b>🏩 Отель:</b> {hotel_data['name']}\n" \
             f"<b>📍 Район:</b> {hotel_data['hotel_neighbourhood']}\n" \
             f"<b>🚕 Расстояние до центра:</b> {hotel_data['distance_city_center']} Км\n" \
             f"<b>💰 Цена за 1 ночь: </b> от {hotel_data['price_per_night']}$\n" \
             f"<b>💰💰 Примерная стоимость за {amount_nights} ноч.:</b> {hotel_data['total_price']}$\n" \
             f"<b>⚓️ Подробнее об отеле <a href='{hotel_data['hotel_url']}'>на сайте >></a></b>"
    return result


@logger.catch
def get_hotel_info_str_nohtml(hotel_data: Dict, amount_nights: int) -> str:
    """
    Функция преобразует данные по отелю из словаря в строку без html.
    Используется для вывода информации через медиа группу (bot.send_media_group).

    :param hotel_data: словарь с информацией по отелю.
    :param amount_nights: количество ночей.
    :return: строка без html с информацией по отелю.
    """

    result = f"🏩 {hotel_data['name']}\n" \
             f"📍 Район: {hotel_data['hotel_neighbourhood']}\n" \
             f"🚕 Расстояние до центра: {hotel_data['distance_city_center']} Км\n" \
             f"💰 Цена за 1 ночь: от {hotel_data['price_per_night']}$\n" \
             f"💰💰 Примерная стоимость за {amount_nights} ноч.: {hotel_data['total_price']}$\n" \
             f"⚓️ Подробнее об отеле: {hotel_data['hotel_url']}"
    return result
