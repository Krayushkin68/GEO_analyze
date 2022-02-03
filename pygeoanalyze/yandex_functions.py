import requests


def request_yandex(request_text, token, bbox=None, is_address_search=False):
    url = 'https://search-maps.yandex.ru/v1/'
    if not is_address_search:
        if not bbox:
            raise Exception('Bbox is not provided for common search')
        params = {
            'apikey': token,
            'bbox': f'{bbox[1]},{bbox[0]}~{bbox[3]},{bbox[2]}',
            'text': request_text,
            'results': 25,
            'rspn': 1,
            'lang': 'ru_RU'
        }
    else:
        params = {
            'apikey': token,
            'text': request_text,
            'results': 1,
            'lang': 'ru_RU'
        }
    headers = {'user-agent': 'Krayushkin app'}
    r = requests.get(url, params=params, headers=headers)
    try:
        if r.status_code == 200:
            data = r.json()
            return parse_response(data)
        else:
            return False
    except (ConnectionError, ConnectionAbortedError, ConnectionRefusedError) as e:
        print(e)
        return False
    except Exception as e:
        print(e)
        return False


def parse_response(data):
    names = []
    coords = []
    for obj in data['features']:
        names.append(obj['properties']['name'])
        coords.append(obj['geometry']['coordinates'])
        # address = obj['properties']['description']
    return names, coords


def get_coords_by_address(address, token):
    response = request_yandex(request_text=address, token=token, is_address_search=True)
    if response:
        _, coords = response
        lon, lat = coords[0]
        return lat, lon
    return False


def request_all_info(bbox, request_info, token):
    received_info = {}
    received_info_coords = {}
    for key, val in request_info.items():
        result_names = []
        result_coords = []
        for el in val:
            names, coords = request_yandex(request_text=el, bbox=bbox, token=token)
            result_names.extend(names)
            result_coords.extend(coords)
        received_info[key] = [len(result_names), list(set(result_names))]
        received_info_coords[key] = [result_coords]
    return received_info, received_info_coords
