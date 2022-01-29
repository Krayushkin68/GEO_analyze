import io
import math
import random
import overpy



import mercantile
import requests
from bs4 import BeautifulSoup as Bs
from cairo import ImageSurface, FORMAT_ARGB32, Context


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


def transform_coords(map: ImageSurface, lon, lat):
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


bs = Bs(open('map3.osm', 'rb').read(), "lxml-xml")

bounds = bs.select('bounds')[0]
west = float(bounds['minlon'])
south = float(bounds['minlat'])
east = float(bounds['maxlon'])
north = float(bounds['maxlat'])
zoom = 15

map_image = get_map(west, south, east, north, zoom)

# Get data from overpass
query = f'[out:xml]; node["highway"="bus_stop"] ({south},{west},{north}, {east}); out;'
res_xml = request_overpass(query)

api = overpy.Overpass()
res_overpy = api.parse_xml(res_xml)

# Paint something
ctx = Context(map_image)
for cafe_coords in res_overpy.nodes:
    x, y = transform_coords(map_image, cafe_coords.lon.__float__(), cafe_coords.lat.__float__())
    ctx.set_source_rgb(255, 0, 0)
    ctx.arc(x, y, 3, 0, 2 * math.pi)
    ctx.stroke()

with open("map.png", "wb") as f:
    map_image.write_to_png(f)



