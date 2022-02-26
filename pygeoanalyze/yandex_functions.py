import asyncio
import random
from collections import defaultdict

import aiohttp
import requests
from fake_useragent import UserAgent


async def check_proxy(proxy, session):
    try:
        async with session.get('https://httpbin.org/get', proxy=proxy, timeout=1) as response:
            if response.status == 200:
                return proxy
    except Exception:
        return None


async def check_proxies(proxies):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for proxy in proxies:
            tasks.append(check_proxy(proxy, session))
        responses = await asyncio.gather(*tasks)
    valid_proxies = [el for el in responses if el]
    return valid_proxies


def get_valid_proxies(proxies):
    valid_proxies = None
    if proxies:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        valid_proxies = asyncio.run(check_proxies(proxies))
    return valid_proxies


def prepare_proxy(proxies, target):
    if not proxies:
        return None

    proxy = random.choice(proxies)
    if target == 'requests':
        requests_proxy = None
        if proxy.startswith('http'):
            requests_proxy = {'http': proxy}
        elif proxy.startswith('https'):
            requests_proxy = {'https': proxy}
        return requests_proxy
    else:
        return proxy


async def check_token(token, session):
    try:
        url, params, headers = prepare_request(request_text='Тест', token=token, is_address_search=True)
        async with session.get(url, params=params, headers=headers, timeout=1) as response:
            if response.status == 200:
                data = await response.json()
                if not (data.get('message') and data.get('message') == 'Invalid key'):
                    return token
    except Exception:
        return None


async def check_tokens(tokens):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for token in tokens:
            tasks.append(check_token(token, session))
        responses = await asyncio.gather(*tasks)
    valid_tokens = [el for el in responses if el]
    return valid_tokens


def get_valid_token(tokens):
    valid_tokens = None
    if tokens:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        valid_tokens = asyncio.run(check_tokens(tokens))
    return valid_tokens


def get_first_valid_token(tokens):
    tokens = [tokens] if isinstance(tokens, str) else tokens
    for token in tokens:
        try:
            url, params, headers = prepare_request(request_text='Тест', token=token, is_address_search=True)
            response = requests.get(url, params=params, headers=headers)
            data = response.json()
            if data.get('message') and data.get('message') == 'Invalid key':
                continue
            else:
                return token
        except Exception:
            continue
    else:
        return False


def get_coords_by_address(address, token, proxies):
    call = prepare_request(request_text=address, token=token, is_address_search=True)
    if call:
        url, params, headers = call

        proxy = prepare_proxy(proxies, 'requests')
        response = requests.get(url, params=params, headers=headers, proxies=proxy)
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
    ua = UserAgent()
    headers = {'user-agent': ua.random}
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


def prepare_async_calls(session, bbox, request_info, token, proxies):
    calls = []
    proxy = prepare_proxy(proxies, 'aiohttp')
    for val in request_info.values():
        for el in val:
            call = prepare_request(request_text=el, bbox=bbox, token=token)
            if call:
                url, params, headers = call
                calls.append(session.get(url=url, params=params, headers=headers, proxy=proxy, ssl=False))
    return calls


async def make_async_calls(bbox, request_info, token, proxies):
    results = []
    async with aiohttp.ClientSession() as session:
        tasks = prepare_async_calls(session, bbox, request_info, token, proxies)
        responses = await asyncio.gather(*tasks)
        for response in responses:
            results.append(await response.json())
    return results


def cleanup_info(data):
    for item in data['supermarkets']:
        if item in data['small_shops']:
            data['small_shops'].remove(item)


def request_all_info_async(bbox, request_info, token, proxies):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    responses = asyncio.run(make_async_calls(bbox, request_info, token, proxies))

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
