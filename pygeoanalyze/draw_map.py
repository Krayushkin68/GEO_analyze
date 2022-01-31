import io
import math
import random

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

    map_image = ImageSurface(FORMAT_ARGB32, tile_size[0] * (max_x - min_x + 1), tile_size[1] * (max_y - min_y + 1))
    ctx = Context(map_image)

    for t in tiles:
        server = random.choice(['a', 'b', 'c'])
        url = 'http://{server}.tile.openstreetmap.org/{zoom}/{x}/{y}.png'.format(server=server, zoom=t.z, x=t.x, y=t.y)
        response = requests.get(url)
        img = ImageSurface.create_from_png(io.BytesIO(response.content))

        ctx.set_source_surface(img, (t.x - min_x) * tile_size[0], (t.y - min_y) * tile_size[0])
        ctx.paint()

    bounds = {
        "left": min([mercantile.xy_bounds(t).left for t in tiles]),
        "right": max([mercantile.xy_bounds(t).right for t in tiles]),
        "bottom": min([mercantile.xy_bounds(t).bottom for t in tiles]),
        "top": max([mercantile.xy_bounds(t).top for t in tiles]),
    }

    kx = map_image.get_width() / (bounds['right'] - bounds['left'])
    ky = map_image.get_height() / (bounds['top'] - bounds['bottom'])

    left_top = mercantile.xy(west, north)
    right_bottom = mercantile.xy(east, south)
    offset_left = (left_top[0] - bounds['left']) * kx
    offset_top = (bounds['top'] - left_top[1]) * ky
    offset_right = (bounds['right'] - right_bottom[0]) * kx
    offset_bottom = (right_bottom[1] - bounds['bottom']) * ky

    map_image_clipped = ImageSurface(FORMAT_ARGB32, map_image.get_width() - int(offset_left + offset_right),
                                     map_image.get_height() - int(offset_top + offset_bottom))

    ctx = Context(map_image_clipped)
    ctx.set_source_surface(map_image, -offset_left, -offset_top)
    ctx.paint()
    return map_image_clipped


def transform_coords(map_img: ImageSurface, coords, lon, lat):
    west, south, north, east = coords

    left_top = mercantile.xy(west, north)
    right_bottom = mercantile.xy(east, south)

    kx = map_img.get_width() / (right_bottom[0] - left_top[0])
    ky = map_img.get_height() / (right_bottom[1] - left_top[1])

    x, y = mercantile.xy(lon, lat)

    x = (x - left_top[0]) * kx
    y = (y - left_top[1]) * ky
    return x, y


def draw(bbox, data: Bs, output_filename="data/map.png"):
    south, west, north, east = [float(el) for el in bbox.split(',')]
    zoom = 15

    map_image = get_map(west, south, east, north, zoom)

    ctx = Context(map_image)
    nodes = [el.parent for el in data.select('node tag')]
    for node in nodes:
        node_x, node_y = float(node.get('lon')), float(node.get('lat'))
        x, y = transform_coords(map_image, [west, south, north, east], node_x, node_y)
        ctx.set_source_rgb(255, 0, 0)
        ctx.arc(x, y, 3, 0, 2 * math.pi)
        ctx.stroke()

    with open(output_filename, "wb") as f:
        map_image.write_to_png(f)
