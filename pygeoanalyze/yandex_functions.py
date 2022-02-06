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
    try:
        r = requests.get(url, params=params, headers=headers)
        data = r.json()
        if r.status_code == 200:
            if not is_address_search:
                return parse_response(data)
            else:
                return data
        elif r.status_code == 403 and data.get('message') == 'Invalid key':
            raise Exception('Invalid token provided')
        else:
            return False
    except (ConnectionError, ConnectionAbortedError, ConnectionRefusedError) as e:
        print(f'Connection error: {e}')
        return False
    except Exception as e:
        print(e)
        return False


def parse_response(data):
    names = []
    coords = []
    json_data = []
    for obj in data['features']:
        name = obj['properties']['name']
        coord = obj['geometry']['coordinates']
        address = obj['properties']['description']
        json_data.append({'name': name, 'address': address, 'coordinates': coord})
        names.append(name)
        coords.append(coord)
    return names, coords, json_data


def get_coords_by_address(address, token):
    response = request_yandex(request_text=address, token=token, is_address_search=True)
    if response and response.get('features'):
        lon, lat = response['features'][0]['geometry']['coordinates']
        return lat, lon
    return False


def request_all_info(bbox, request_info, token):
    received_info = {}
    received_info_coords = {}
    received_info_json = []
    for key, val in request_info.items():
        result_names = []
        result_coords = []
        result_json = []
        for el in val:
            result = request_yandex(request_text=el, bbox=bbox, token=token)
            if result:
                names, coords, json_data = result
                result_names.extend(names)
                result_coords.extend(coords)
                result_json.extend(json_data)
            else:
                return False
        received_info[key] = [len(result_names), list(set(result_names))]
        received_info_coords[key] = [result_coords]
        received_info_json.append({'category': key, 'count': len(json_data), 'items': json_data})
    return received_info, received_info_coords, received_info_json
