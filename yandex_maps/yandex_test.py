import json

import requests

TOKEN = json.load(open('token.json', 'rt')).get('TOKEN')

url = 'https://search-maps.yandex.ru/v1/'

bbox = [55.70086, 37.94424, 55.71526, 37.96922]
request_text = 'Аптека'
params = {
    'apikey': TOKEN,
    'bbox': f'{bbox[1]},{bbox[0]}~{bbox[3]},{bbox[2]}',
    'text': request_text,
    'results': 25,
    'rspn': 1,
    'lang': 'ru_RU'
}
headers = {'user-agent': 'Krayushkin app'}

r = requests.get(url, params=params, headers=headers)
data = r.json()

search_objects = []
for obj in data['features']:
    name = obj['properties']['name']
    address = obj['properties']['description']
    coords = obj['geometry']['coordinates']
    search_objects.append([name, address, coords])

[print(i) for i in search_objects]
