import os
import json
from pygeoanalyze.osm_analyzer import OSMAnalyzer
from pygeoanalyze.yandex_analyzer import YandexAnalyzer


class Infrastructure:
    def __init__(self, source, address=None, lat=None, lon=None, search_range=500, token=None):
        if source == 'Yandex':
            self.analyzer = YandexAnalyzer(token)
        else:
            self.analyzer = OSMAnalyzer()

        if address:
            self.set_address(address)
        if lat and lon:
            self.set_coordinates(lat, lon)
        if search_range:
            self.set_search_range(search_range)

        self.received_info = dict()
        self.received_info_json = []

    def set_address(self, address):
        self.analyzer.set_address(address)

    def set_coordinates(self, lat: float, lon: float):
        if not (isinstance(lat, float) or isinstance(lon, float)):
            raise TypeError('Coordinates must be float')
        if not (round(lat) in range(-90, 91) or round(lon) in range(-180, 181)):
            raise ValueError('Latitude should be from -90 to 90 degrees. '
                             'Longitude should be from -180 to 180 degrees.')
        self.analyzer.set_coordinates(lat, lon)

    def set_search_range(self, search_range: int):
        if not isinstance(search_range, int):
            raise TypeError('Search range must be int')
        self.analyzer.set_search_range(search_range)

    def analyze(self):
        result = self.analyzer.analyze()
        if result:
            self.received_info, self.received_info_json = result
            return True
        return False

    def clear(self):
        self.received_info = dict()
        self.received_info_json = []
        self.analyzer.clear()

    def save_to_xml(self, output_filename):
        if not self.received_info:
            raise RuntimeError('Data is empty. Try run .analyze() method.')
        try:
            if os.path.dirname(output_filename) and not os.path.exists(os.path.dirname(output_filename)):
                os.makedirs(os.path.dirname(output_filename))
            self.analyzer.save_to_xml(output_filename)
        except Exception as e:
            print(e)
            return False

    def save_to_json(self, output_filename):
        if not self.received_info_json:
            raise RuntimeError('Data is empty. Try run .analyze() method.')
        try:
            if os.path.dirname(output_filename) and not os.path.exists(os.path.dirname(output_filename)):
                os.makedirs(os.path.dirname(output_filename))
            json.dump(self.received_info_json, open(output_filename, 'wt', encoding='utf-8'), ensure_ascii=False, indent=4)
        except Exception as e:
            print(e)
            return False

    def draw_map(self, output_filename):
        if not self.received_info:
            raise RuntimeError('Data is empty. Try run .analyze() method.')
        try:
            if os.path.dirname(output_filename) and not os.path.exists(os.path.dirname(output_filename)):
                os.makedirs(os.path.dirname(output_filename))
            self.analyzer.draw_map(output_filename)
        except Exception as e:
            print(e)
            return False
