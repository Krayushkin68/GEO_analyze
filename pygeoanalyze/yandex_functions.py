import asyncio
from collections import defaultdict

import aiohttp
import requests


def get_coords_by_address(address, token):
    call = prepare_request(request_text=address, token=token, is_address_search=True)
    if call:
        url, params, headers = call
        response = requests.get(url, params=params, headers=headers)
        data = response.json()

        if data.get('message') and data.get('message') == 'Invalid key':
            raise Exception('Invalid token provided')

        if data and data.get('features'):
            lon, lat = data['features'][0]['geometry']['coordinates']
            return lat, lon
    return False


def prepare_request(request_text, token, bbox=None, is_address_search=False):
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
    return url, params, headers


def process_response(data):
    if data.get('message') and data.get('message') == 'Invalid key':
        raise Exception('Invalid token provided')

    request_key = data['properties']['ResponseMetaData']['SearchRequest']['request']
    res_data = []
    for obj in data['features']:
        name = obj['properties']['name']
        coord = obj['geometry']['coordinates']
        address = obj['properties']['description']
        res_data.append({'name': name, 'address': address, 'coordinates': coord})
    return request_key, res_data


def prepare_async_calls(session, bbox, request_info, token):
    calls = []
    for val in request_info.values():
        for el in val:
            call = prepare_request(request_text=el, bbox=bbox, token=token)
            if call:
                url, params, headers = call
                calls.append(session.get(url=url, params=params, headers=headers))
    return calls


async def make_async_calls(bbox, request_info, token):
    results = []
    async with aiohttp.ClientSession() as session:
        tasks = prepare_async_calls(session, bbox, request_info, token)
        responses = await asyncio.gather(*tasks)
        for response in responses:
            results.append(await response.json())
    return results


def cleanup_info(data):
    for item in data['supermarkets']:
        if item in data['small_shops']:
            data['small_shops'].remove(item)


def request_all_info_async(bbox, request_info, token):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    responses = asyncio.run(make_async_calls(bbox, request_info, token))

    import pickle
    pickle.dump(responses, open('data/data.pkl', 'wb'))

    received_info = defaultdict(lambda: [])
    for response in responses:
        request_key, el_data = process_response(response)
        dict_key = [k for k, v in request_info.items() if request_key in v][0]
        received_info[dict_key].extend(el_data)

    cleanup_info(received_info)

    result_info = []
    for key, val in received_info.items():
        result_info.append({'category': key, 'count': len(val), 'items': val})

    return result_info
