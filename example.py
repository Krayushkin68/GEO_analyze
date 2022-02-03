from pygeoanalyze import Infrastructure
import json

TOKEN = json.load(open('token.json', 'rt')).get('TOKEN')

inf_osm = Infrastructure(address='Люберцы, Барыкина 8', search_range=800, source='OSM')
if inf_osm.analyze():
    print(inf_osm.received_info)
    inf_osm.save_to_xml('data/map.xml')
    inf_osm.draw_map('data/map.png')

inf_ya = Infrastructure(address='Люберцы, Барыкина 8', search_range=500, source='Yandex', token=TOKEN)
if inf_ya.analyze():
    print(inf_ya.received_info)
    inf_ya.draw_map('data/map_ya.png')
