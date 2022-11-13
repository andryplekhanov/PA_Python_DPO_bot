from typing import Dict, List, Union
from utils.api_reqiest import request_to_api
from config_data.config import RAPID_API_HEADERS, RAPID_API_ENDPOINTS
import json


def parse_photos(hotel_id: int) -> Union[List[Dict], None]:
    """
    Функция делает запрос в request_to_api и десериализирует результат. Если запрос получен и десериализация прошла -
    возвращает обработанный результат в виде списка словарей, иначе None.

    :param hotel_id: id отеля для запроса по api.
    :return: None или список словарей с полной информацией по фоткам отеля.
    """

    querystring = {"id": hotel_id}
    responce = request_to_api(
        url=RAPID_API_ENDPOINTS['hotel-photos'],
        querystring=querystring,
        headers=RAPID_API_HEADERS)
    if responce and responce.text != '':  # responce.text == '' - это когда у отеля нет фоток, хотя responce == 200
        result = json.loads(responce.text).get('hotelImages')
        return result
    return None


def process_photos(all_photos: List[Dict], amount_photos: int) -> Union[List[str], None]:
    """
    Функция получает список словарей - результат парсинга фоток, выбирает нужную информацию, обрабатывает и складывает
    в список result.

    :param all_photos: список словарей с полной информацией по фоткам отеля.
    :param amount_photos: количество фотографий.
    :return: result - список заданной в amount_photos длины с url фоток.
    """

    photos = all_photos[:amount_photos]
    result = list()
    for photo in photos:
        try:
            url = photo.get('baseUrl')
            suffix = [size.get('suffix') if size.get('suffix') in ('z', 'w') else size.get('suffix')
                      for size in photo.get('sizes')][0]
            result.append(url.format(size=suffix))
        except Exception:
            result = None
    return result
