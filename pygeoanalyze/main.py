import os

from geopy.geocoders import Nominatim

from pygeoanalyze.draw_map import draw
from pygeoanalyze.static_functions import *


class Infrastructure:
    def __init__(self, address=None, lat=None, lon=None, search_range=500):
        self.address = str()
        self.lat = float()
        self.lon = float()
        self.search_range = search_range
        if address:
            self.set_address(address)
        if lat and lon:
            self.set_coordinates(lat, lon)
        if search_range != 500:
            self.set_search_range(search_range)

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
        self.recieved_info = dict()
        self._bbox = None
        self._recieved_data = None

    def set_address(self, address):
        self.address = address

    def set_coordinates(self, lat: float, lon: float):
        if not (isinstance(lat, float) or isinstance(lon, float)):
            raise TypeError('Coordinates must be float')
        if not (round(lat) in range(-90, 91) or round(lon) in range(-180, 181)):
            raise ValueError('Lattitude should be from -90 to 90 degrees. '
                             'Longtitude should be from -180 to 180 degrees.')
        self.lat = lat
        self.lon = lon

    def set_search_range(self, search_range: int):
        if not isinstance(search_range, int):
            raise TypeError('Search range must be int')
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
        self._recieved_data = request_overpass(self._bbox, self.request_info)
        if self._recieved_data:
            self.recieved_info = analyze_response(self._recieved_data, self.request_info)
            return True if self.recieved_info else False
        return False

    def save_to_xml(self, output_filename):
        if not self._recieved_data:
            raise RuntimeError('Data is empty. Try run .analyze() method.')
        try:
            if os.path.dirname(output_filename) and not os.path.exists(os.path.dirname(output_filename)):
                os.makedirs(os.path.dirname(output_filename))
            with open(output_filename, "wt", encoding='utf-8') as f:
                f.write(str(self._recieved_data))
        except Exception as e:
            print(e)
            return False

    def draw_map(self, output_filename):
        if not self._recieved_data:
            raise RuntimeError('Data is empty. Try run .analyze() method.')
        try:
            if os.path.dirname(output_filename) and not os.path.exists(os.path.dirname(output_filename)):
                os.makedirs(os.path.dirname(output_filename))
            draw(self._bbox, self._recieved_data, output_filename)
        except Exception as e:
            print(e)
            return False
