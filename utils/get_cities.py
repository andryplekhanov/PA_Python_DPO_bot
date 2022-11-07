from typing import Dict
from utils.api_reqiest import request_to_api
from config_data.config import RAPID_API_HEADERS, RAPID_API_ENDPOINTS
import re
import json


def parse_cities_group(city: str) -> Dict[str, str] or None:
    querystring = {"query": city, "locale": "ru_RU", "currency": "USD"}
    responce = request_to_api(
        url=RAPID_API_ENDPOINTS['cities-groups'],
        querystring=querystring,
        headers=RAPID_API_HEADERS)

    if responce:
        pattern = r'(?<="CITY_GROUP",).+?[\]]'
        find = re.search(pattern, responce.text)
        if find:
            cities = dict()
            try:
                result = json.loads(f"{{{find[0]}}}")
                for entity in result.get('entities'):
                    if entity.get('type') == 'CITY':
                        pattern = r'\<(/?[^>]+)>'
                        city_clear_name = re.sub(pattern, '', entity.get('caption', {}))
                        cities[city_clear_name] = entity.get('destinationId')
            except Exception:
                cities = None
            return cities
    return None
