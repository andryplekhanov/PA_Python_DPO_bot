from typing import Dict, List, Union
from utils.api_reqiest import request_to_api
from config_data.config import RAPID_API_HEADERS, RAPID_API_ENDPOINTS
import json


def parse_photos(hotel_id: int) -> Union[List[Dict], None]:
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
