from math import cos

import requests
from bs4 import BeautifulSoup as Bs

D_LAT = 111134.861111
D_LON = 111321.377778

TAGS_FOOD = ['amenity', ['cafe', 'fast_food', 'food_court', 'restaurant']]
TAGS_DRINK = ['amenity', ['bar', 'biergarten', 'pub']]
TAGS_EDUCATION = ['amenity', ['kindergarten', 'school']]
TAGS_PUBLIC_TRANSPORT_ROAD = ['highway', ['bus_stop', 'platform']]
TAGS_PUBLIC_TRANSPORT_STATIONS = ['public_transport', ['bus_stop', 'stop_position', 'platform', 'station', 'stop_area']]
TAGS_PERSONAL_TRANSPORT = ['amenity', ['parking', 'parking_space', 'car_wash']]
TAGS_FINANCE = ['amenity', ['atm', 'bank']]
TAGS_HOSPITAL = ['amenity', ['clinic', 'hospital']]
TAGS_PHARMACY = ['amenity', ['pharmacy']]
TAGS_ENTERTAINMENT = ['amenity', ['arts_centre', 'cinema', 'theatre']]
SHOP_MALL = ['shop', ['department_store', 'mall']]
SHOP_SUPERMARKET = ['shop', ['supermarket']]
SHOP_SMALLSHOP = ['shop', ['convenience']]


def get_bbox(lat, lon, radius):
    r_lat = radius / D_LAT
    r_lon = radius / (D_LON * abs(cos(D_LON)))

    south = round(min(lat - r_lat, lat + r_lat), 5)
    north = round(max(lat - r_lat, lat + r_lat), 5)
    west = round(min(lon - r_lon, lon + r_lon), 5)
    east = round(max(lon - r_lon, lon + r_lon), 5)
    return [south, west, north, east]


def create_query(bbox, tags):
    bbox = ','.join([str(el) for el in bbox])
    search_part = []
    for base_tag, search_tags in tags:
        for tag in search_tags:
            search_part.append(f'node["{base_tag}"="{tag}"]({bbox});')
            search_part.append(f'way["{base_tag}"="{tag}"]({bbox});')
    query = f'[out:xml][timeout:15]; ({" ".join(search_part)}); (._;>;); out;'
    return query


def select_nodes_by_tags(bs, tags):
    base_tag, search_tags = tags
    nodes = []
    for tag in search_tags:
        nodes.extend([t.parent for t in bs.select(f'tag[k="{base_tag}"][v="{tag}"]')])
    return nodes


def request_overpass(bbox, item):
    query = create_query(bbox, list(item.values()))

    useragent = 'Krayushkin_OSM'
    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Google Chrome 80"',
        'Accept': '*/*',
        'Sec-Fetch-Dest': 'empty',
        'User-Agent': useragent,
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://overpass-turbo.eu',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Referer': 'https://overpass-turbo.eu/',
        'Accept-Language': '',
        'dnt': '1',
    }

    data = {'data': query}
    try:
        response = requests.post('https://overpass-api.de/api/interpreter', headers=headers, data=data)
        if response.status_code == 200:
            bs = Bs(response.text, "lxml-xml")
            return bs
        return False
    except (ConnectionError, ConnectionAbortedError, ConnectionRefusedError) as e:
        print(e)
        return False
    except Exception as e:
        print(e)
        return False


def analyze_response(data, item):
    for el, tags in item.items():
        nodes = select_nodes_by_tags(data, tags)
        count = len(nodes)
        names = [n.select('tag[k="name"]')[0].get('v') for n in nodes if n.select('tag[k="name"]')]
        names = list(set(names))
        item[el] = [count, names]
    return item
