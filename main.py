import io
import math
import random
from math import cos

import mercantile
import requests
from bs4 import BeautifulSoup as Bs
from cairo import ImageSurface, FORMAT_ARGB32, Context
from geopy.geocoders import Nominatim

D_LAT = 111134.861111
D_LON = 111321.377778


def get_map(west, south, east, north, zoom):
    tiles = list(mercantile.tiles(west, south, east, north, zoom))

    min_x = min([t.x for t in tiles])
    min_y = min([t.y for t in tiles])
    max_x = max([t.x for t in tiles])
    max_y = max([t.y for t in tiles])

    tile_size = (256, 256)
    # создаем пустое изображение в которое как мозайку будем вставлять тайлы
    map_image = ImageSurface(
        FORMAT_ARGB32,
        tile_size[0] * (max_x - min_x + 1),
        tile_size[1] * (max_y - min_y + 1)
    )

    ctx = Context(map_image)

    for t in tiles:
        server = random.choice(['a', 'b', 'c'])
        url = 'http://{server}.tile.openstreetmap.org/{zoom}/{x}/{y}.png'.format(
            server=server,
            zoom=t.z,
            x=t.x,
            y=t.y
        )
        response = requests.get(url)
        img = ImageSurface.create_from_png(io.BytesIO(response.content))

        ctx.set_source_surface(
            img,
            (t.x - min_x) * tile_size[0],
            (t.y - min_y) * tile_size[0]
        )
        ctx.paint()

    # расчитываем коэффициенты
    bounds = {
        "left": min([mercantile.xy_bounds(t).left for t in tiles]),
        "right": max([mercantile.xy_bounds(t).right for t in tiles]),
        "bottom": min([mercantile.xy_bounds(t).bottom for t in tiles]),
        "top": max([mercantile.xy_bounds(t).top for t in tiles]),
    }

    # коэффициенты скалирования по оси x и y
    kx = map_image.get_width() / (bounds['right'] - bounds['left'])
    ky = map_image.get_height() / (bounds['top'] - bounds['bottom'])

    # пересчитываем размеры по которым будем обрезать
    left_top = mercantile.xy(west, north)
    right_bottom = mercantile.xy(east, south)
    offset_left = (left_top[0] - bounds['left']) * kx
    offset_top = (bounds['top'] - left_top[1]) * ky
    offset_right = (bounds['right'] - right_bottom[0]) * kx
    offset_bottom = (right_bottom[1] - bounds['bottom']) * ky

    # обрезанное изображение
    map_image_clipped = ImageSurface(
        FORMAT_ARGB32,
        map_image.get_width() - int(offset_left + offset_right),
        map_image.get_height() - int(offset_top + offset_bottom),
    )

    # вставляем кусок исходного изображения
    ctx = Context(map_image_clipped)
    ctx.set_source_surface(map_image, -offset_left, -offset_top)
    ctx.paint()

    return map_image_clipped


def transform_coords(map: ImageSurface, coords, lon, lat):
    west, south, north, east = coords
    # рассчитываем координаты углов в веб-меркаоторе
    leftTop = mercantile.xy(west, north)
    rightBottom = mercantile.xy(east, south)

    # расчитываем коэффициенты
    kx = map.get_width() / (rightBottom[0] - leftTop[0])
    ky = map.get_height() / (rightBottom[1] - leftTop[1])

    x, y = mercantile.xy(lon, lat)

    # переводим x, y в координаты изображения
    x = (x - leftTop[0]) * kx
    y = (y - leftTop[1]) * ky
    return x, y


def request_overpass(query):
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
    response = requests.post('https://overpass-api.de/api/interpreter', headers=headers, data=data)
    return response.text


def paint(bbox, osm_data):
    south, west, north, east = [float(el) for el in bbox.split(',')]
    zoom = 15

    map_image = get_map(west, south, east, north, zoom)

    ctx = Context(map_image)
    nodes = [el.parent for el in osm_data.select('node tag')]
    for node in nodes:
        node_x, node_y = float(node.get('lon')), float(node.get('lat'))
        x, y = transform_coords(map_image, [west, south, north, east], node_x, node_y)
        ctx.set_source_rgb(255, 0, 0)
        ctx.arc(x, y, 3, 0, 2 * math.pi)
        ctx.stroke()

    with open("data/map.png", "wb") as f:
        map_image.write_to_png(f)


def get_bbox(lat, lon, radius):
    south = lat - round(radius / D_LAT, 5)
    west = lon - round(radius / (D_LON * abs(cos(D_LON))), 5)
    north = lat + round(radius / D_LAT, 5)
    east = lon + round(radius / (D_LON * abs(cos(D_LON))), 5)
    return f'{south}, {west}, {north}, {east}'


def create_query(bbox, tags):
    search_part = []
    for base_tag, search_tags in tags:
        for tag in search_tags:
            search_part.append(f'node["{base_tag}"="{tag}"]({bbox});')
            search_part.append(f'way["{base_tag}"="{tag}"]({bbox});')
    query = f'[out:xml]; ({" ".join(search_part)}); (._;>;); out;'
    return query


def select_nodes_by_tags(bs, tags):
    base_tag, search_tags = tags
    nodes = []
    for tag in search_tags:
        nodes.extend([t.parent for t in bs.select(f'tag[k="{base_tag}"][v="{tag}"]')])
    return nodes


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

# address = "Люберцы Барыкина 4"
address = "Москва, улица Молдагуловой, д. 8к1"
geolocator = Nominatim(user_agent='Krayushkin app')
location = geolocator.geocode(address)
if not location:
    print('No such location')
lat = location.latitude
lon = location.longitude
range = 500
bbox = get_bbox(lat, lon, range)

item = {'food': TAGS_FOOD,
        'education': TAGS_EDUCATION,
        'public_transport': TAGS_PUBLIC_TRANSPORT_ROAD,
        'personal_transport': TAGS_PERSONAL_TRANSPORT,
        'finance': TAGS_FINANCE,
        'pharmacy': TAGS_PHARMACY,
        'entertainment': TAGS_ENTERTAINMENT,
        'malls': SHOP_MALL,
        'supermarkets': SHOP_SUPERMARKET,
        'small_shops': SHOP_SMALLSHOP}

query = create_query(bbox, list(item.values()))
xml = request_overpass(query)
bs = Bs(xml, "lxml-xml")

paint(bbox, bs)

with open('data/map.xml', 'wt', encoding='utf-8') as f:
    f.write(xml)

for el, tags in item.items():
    nodes = select_nodes_by_tags(bs, tags)
    count = len(nodes)
    names = [n.select('tag[k="name"]')[0].get('v') for n in nodes if n.select('tag[k="name"]')]
    names = list(set(names))
    item[el] = [count, names]

