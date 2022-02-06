from geopy.geocoders import Nominatim

from pygeoanalyze.draw_map import draw
from pygeoanalyze.osm_functions import *


class OSMAnalyzer:
    def __init__(self):
        self.address = str()
        self.lat = float()
        self.lon = float()
        self.search_range = int()
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
        self.received_info = dict()
        self.received_info_json = []
        self._bbox = None
        self._received_data = None

    def clear(self):
        self.lat = float()
        self.lon = float()
        self.address = str()
        self.search_range = 500
        self.received_info = dict()
        self.received_info_json = []
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
        self._received_data = request_overpass(self._bbox, self.request_info)
        if self._received_data:
            self.received_info, self.received_info_json = analyze_response(self._received_data, self.request_info)
            return self.received_info, self.received_info_json
        return False

    def save_to_xml(self, output_filename):
        with open(output_filename, "wt", encoding='utf-8') as f:
            f.write(str(self._received_data))

    def draw_map(self, output_filename):
        nodes = [[el.parent.get('lon'), el.parent.get('lat')] for el in self._received_data.select('node tag')]
        draw(self._bbox, nodes, output_filename)
