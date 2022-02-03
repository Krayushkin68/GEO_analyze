from pygeoanalyze.draw_map import draw
from pygeoanalyze.osm_functions import get_bbox
from pygeoanalyze.yandex_functions import *


class YandexAnalyzer:
    def __init__(self, token):
        if not token:
            raise ValueError('Need to specify API TOKEN to use Yandex Maps API.')
        self._token = token
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
        self.received_info_coords = dict()
        self._bbox = None
        self._received_data = None

    def set_address(self, address):
        self.address = address

    def set_coordinates(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon

    def set_search_range(self, search_range: int):
        self.search_range = search_range

    def analyze(self):
        if not (self.address or (self.lat and self.lon)):
            raise Exception('Need to specify address or coordinates. Use ".set_address()" or ".set_coordinates()"')
        if self.address:
            location = get_coords_by_address(self.address, self._token)
            if location:
                self.lat, self.lon = location
            else:
                if not (self.lat and self.lon):
                    raise Exception('Cant find location for this address. '
                                    'Please specify another address or use coordinates.')

        self._bbox = get_bbox(self.lat, self.lon, self.search_range)

        request_result = request_all_info(self._bbox, self.request_info, self._token)
        if request_result:
            self.received_info, self.received_info_coords = request_result
            return self.received_info
        return False

    def save_to_xml(self, output_filename):
        print('XML can only be generated from OSM source')

    def draw_map(self, output_filename):
        nodes = []
        for el in self.received_info_coords.values():
            nodes.extend(el[0])
        draw(self._bbox, nodes, output_filename)
