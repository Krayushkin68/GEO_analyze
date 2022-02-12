from geopy.geocoders import Nominatim

from pygeoanalyze.draw_map import draw
from pygeoanalyze.osm_functions import *
from pygeoanalyze.yandex_functions import get_valid_proxies


class OSMAnalyzer:
    def __init__(self):
        self.address = str()
        self.lat = float()
        self.lon = float()
        self.search_range = int()
        self._proxies = []
        self.request_info = {'food': TAGS_FOOD,
                             'education': TAGS_EDUCATION,
                             'public_transport': TAGS_PUBLIC_TRANSPORT_ROAD,
                             'personal_transport': TAGS_PERSONAL_TRANSPORT,
                             'finance': TAGS_FINANCE,
                             'pharmacy': TAGS_PHARMACY,
                             'entertainment': TAGS_ENTERTAINMENT,
                             'malls': SHOP_MALL,
                             'supermarkets': SHOP_SUPERMARKET,
                             'small_shops': SHOP_SMALLSHOP}
        self.received_info = []
        self._bbox = None
        self._received_data = None

    def clear(self):
        self.lat = float()
        self.lon = float()
        self.address = str()
        self.search_range = 500
        self.received_info = []
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
        if self.address:
            geolocator = Nominatim(user_agent='Krayushkin app')
            location = geolocator.geocode(self.address)
            if location:
                self.lat = location.latitude
                self.lon = location.longitude
            else:
                if not (self.lat and self.lon):
                    raise Exception('Cant find location for this address. '
                                    'Please specify another address or use coordinates.')

        self._bbox = get_bbox(self.lat, self.lon, self.search_range)

        proxies = get_valid_proxies(self._proxies)
        self._received_data = request_overpass(self._bbox, self.request_info, proxies)
        if self._received_data:
            self.received_info = analyze_response(self._received_data, self.request_info)
            return self.received_info
        return False

    def save_to_xml(self, output_filename):
        with open(output_filename, "wt", encoding='utf-8') as f:
            f.write(str(self._received_data))

    def draw_map(self, output_filename):
        nodes = []
        for category in self.received_info:
            for item in category['items']:
                if item['coordinates'][0]:
                    nodes.append(item['coordinates'])
        draw(self._bbox, nodes, output_filename)
