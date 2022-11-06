from utils.api_reqiest import request_to_api
from config_data.config import RAPID_API_HEADERS, RAPID_API_ENDPOINTS
import re
import json


def parse_hotels(data_dict):
    querystring = {
        "destinationId": data_dict['city_id'],
        "pageNumber": "1", "pageSize": data_dict['amount_hotels'],
        "checkIn": data_dict['start_date'], "checkOut": data_dict['end_date'],
        "adults1": "1", "sortOrder": "PRICE", "locale": "ru_RU", "currency": "USD"}
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


def process_hotels_info(hotels_info_list, amount_nights):
    hotels_info_dict = dict()
    for hotel in hotels_info_list:
        hotel_id = hotel['id']
        hotel_name = hotel['name']
        price_per_night = hotel['ratePlan']['price']['exactCurrent']
        total_price = round(price_per_night * amount_nights, 2)
        distance_city_center = [
            landmark['distance'] for landmark in hotel['landmarks']
            if landmark['label'] == 'Центр города' or landmark['label'] == 'City center'][0]
        hotel_url = 'https://www.hotels.com/ho' + str(hotel_id) + '/'
        hotel_neighbourhood = hotel['neighbourhood']

        hotels_info_dict[hotel_id] = {
            'name': hotel_name,
            'price_per_night': price_per_night,
            'total_price': total_price,
            'distance_city_center': distance_city_center,
            'hotel_url': hotel_url,
            'hotel_neighbourhood': hotel_neighbourhood
        }
    return hotels_info_dict


def get_hotel_info_str(hotel_data, amount_nights):
    result = f"<b>Отель:</b> {hotel_data['name']}\n" \
            f"<b>Район:</b> {hotel_data['hotel_neighbourhood']}\n" \
            f"<b>Расстояние до центра:</b> {hotel_data['distance_city_center']}\n" \
            f"<b>Цена за 1 ночь: </b> от {hotel_data['price_per_night']}$\n" \
            f"<b>Примерная стоимость за {amount_nights} ночей:</b> {hotel_data['total_price']}$\n" \
            f"<b>Подробнее об отеле смотрите <a href='{hotel_data['hotel_url']}'>на сайте >></a></b>"
    return result
