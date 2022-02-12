import random

from pygeoanalyze.draw_map import draw
from pygeoanalyze.osm_functions import get_bbox
from pygeoanalyze.yandex_functions import *


class YandexAnalyzer:
    def __init__(self, token):
        if not token:
            raise ValueError('Need to specify API TOKEN to use Yandex Maps API.')
        self._token = token
        self._proxies = []
        self.address = str()
        self.lat = float()
        self.lon = float()
        self.search_range = int()
        self.request_info = {'food': ['Кафе'],
                             'education': ['Образование'],
                             'public_transport': ['Станция метро', 'Остановка общественного транспорта'],
                             'personal_transport': ['Автомобильная парковка'],
                             'finance': ['Банкомат'],
                             'pharmacy': ['Аптека'],
                             'entertainment': ['Развлечения'],
                             'malls': ['Торговый центр'],
                             'supermarkets': ['Супермаркет'],
                             'small_shops': ['Магазин']}
        self.received_info = dict()
        self._bbox = None
        self._received_data = None

    def clear(self):
        self.lat = float()
        self.lon = float()
        self.address = str()
        self.search_range = 500
        self.received_info = dict()
        self._bbox = None
        self._received_data = None

    def set_address(self, address):
        self.address = address

    def set_coordinates(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon

    def set_search_range(self, search_range: int):
        self.search_range = search_range

    def add_proxies(self, proxies):
        if isinstance(proxies, str):
            self._proxies.append(proxies)
        elif isinstance(proxies, list):
            self._proxies.extend(proxies)

    def analyze(self):
        if not (self.address or (self.lat and self.lon)):
            raise Exception('Need to specify address or coordinates. Use ".set_address()" or ".set_coordinates()"')

        valid_tokens = get_valid_token(self._token)
        if not valid_tokens:
            raise Exception('No valid token provided')
        valid_token = random.choice(valid_tokens)

        proxies = get_valid_proxies(self._proxies)

        if self.address:
            location = get_coords_by_address(self.address, valid_token, proxies)
            if location:
                self.lat, self.lon = location
            else:
                if not (self.lat and self.lon):
                    raise Exception('Cant find location for this address. '
                                    'Please specify another address or use coordinates.')

        self._bbox = get_bbox(self.lat, self.lon, self.search_range)

        request_result = request_all_info_async(self._bbox, self.request_info, valid_token, proxies)
        if request_result:
            self.received_info = request_result
            return self.received_info
        return False

    def save_to_xml(self, output_filename):
        print('XML can only be generated from OSM source')

    def draw_map(self, output_filename):
        nodes = []
        for category in self.received_info:
            for item in category['items']:
                nodes.append(item['coordinates'])
        draw(self._bbox, nodes, output_filename)
