from typing import Dict, List, Union
from utils.api_reqiest import request_to_api
from config_data.config import RAPID_API_HEADERS, RAPID_API_ENDPOINTS
import re
import json


def parse_hotels(data_dict: Dict[str, Dict[str, str]]) -> Union[Dict[str, List[Dict]], None]:
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


def process_hotels_info(hotels_info_list: List[Dict], amount_nights: int) -> Dict:
    hotels_info_dict = dict()

    for hotel in hotels_info_list:
        hotel_id = hotel.get('id')
        if not hotel_id:
            continue
        hotel_url = f'https://www.hotels.com/ho{str(hotel_id)}/'
        hotel_name = hotel.get('name', 'No name')
        price_per_night = hotel.get('ratePlan', {}).get('price', {}).get('exactCurrent', 0)
        total_price = round(price_per_night * amount_nights, 2)

        distance_city_center = None
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
    return hotels_info_dict  # теоретически может быть пустым


def get_hotel_info_str(hotel_data: Dict, amount_nights: int) -> str:
    result = f"<b>🏩 Отель:</b> {hotel_data['name']}\n" \
            f"<b>📍 Район:</b> {hotel_data['hotel_neighbourhood']}\n" \
            f"<b>🚕 Расстояние до центра:</b> {hotel_data['distance_city_center']} Км\n" \
            f"<b>💰 Цена за 1 ночь: </b> от {hotel_data['price_per_night']}$\n" \
            f"<b>💰💰 Примерная стоимость за {amount_nights} ноч.:</b> {hotel_data['total_price']}$\n" \
            f"<b>⚓️ Подробнее об отеле <a href='{hotel_data['hotel_url']}'>на сайте >></a></b>"
    return result
