import requests


def request_to_api(url, querystring, headers):
    try:
        request = requests.get(url=url, params=querystring, headers=headers, timeout=10)
        if request.status_code == requests.codes.ok:
            return request
    except Exception as exc:
        return None
