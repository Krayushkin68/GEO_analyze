import json

from pygeoanalyze import Infrastructure

TOKEN = json.load(open('token.json', 'rt')).get('TOKEN')

# EXAMPLE 1
inf_osm = Infrastructure(address='Люберцы, Барыкина 8', search_range=800, source=Infrastructure.sources.OSM)
if inf_osm.analyze():
    print(inf_osm.received_info)
    inf_osm.save_to_xml('data/map_osm.xml')
    inf_osm.save_to_json('data/map_osm.json')
    inf_osm.draw_map('data/map_osm.png')

# EXAMPLE 2
inf_ya = Infrastructure(address='Люберцы, Барыкина 8', search_range=500, source=Infrastructure.sources.Yandex,
                        token=TOKEN)
if inf_ya.analyze():
    print(inf_ya.received_info)
    inf_ya.save_to_json('data/map_ya.json')
    inf_ya.draw_map('data/map_ya.png')

# EXAMPLE 3
interested_addresses = [
    'Москва, ул. Юных Ленинцев 38',
    'Москва, 2-й Карачаровский проезд, 4',
    'Москва, Нижегородская улица, 13А',
    'Москва, Рабочая улица, 6к1'
]
inf = Infrastructure(source=Infrastructure.sources.Yandex, token=TOKEN, search_range=500)
data = dict().fromkeys(interested_addresses)
for addr in interested_addresses:
    inf.set_address(addr)
    if inf.analyze():
        data[addr] = inf.received_info
    inf.clear()
json.dump(data, open('data/interested_data.json', 'wt', encoding='utf-8'), ensure_ascii=False, indent=4)
