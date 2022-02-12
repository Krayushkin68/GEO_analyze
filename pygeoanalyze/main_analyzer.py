import json
import os

from pygeoanalyze.osm_analyzer import OSMAnalyzer
from pygeoanalyze.yandex_analyzer import YandexAnalyzer


class Sources:
    OSM = 'OSM'
    Yandex = 'Yandex'
    sources = [OSM, Yandex]


class Infrastructure:
    sources = Sources()

    def __init__(self, source, address=None, lat=None, lon=None, search_range=500, token=None):
        self.analyzer = self._set_source(source, token)
        if address:
            self.set_address(address)
        if lat and lon:
            self.set_coordinates(lat, lon)
        if search_range:
            self.set_search_range(search_range)

        self.received_info = []

    def _set_source(self, source, token):
        if source == 'Yandex':
            return YandexAnalyzer(token)
        elif source in ('OSM', None):
            return OSMAnalyzer()
        else:
            print(f'Requested source "{source}" is not availible.\n'
                  f'Currently availible sources are: {self.sources.sources}\n'
                  f'Setting default source: "OSM"')
            return OSMAnalyzer()

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
            self.received_info = result
            return True
        return False

    def clear(self):
        self.received_info = []
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
        if not self.received_info:
            raise RuntimeError('Data is empty. Try run .analyze() method.')
        try:
            if os.path.dirname(output_filename) and not os.path.exists(os.path.dirname(output_filename)):
                os.makedirs(os.path.dirname(output_filename))
            json.dump(self.received_info, open(output_filename, 'wt', encoding='utf-8'), ensure_ascii=False, indent=4)
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
