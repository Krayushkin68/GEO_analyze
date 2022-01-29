import requests

lat = 37.956305
lon = 55.707932
west, south, north, east = 37.9012, 55.6953, 55.718, 37.9665
z = 16
url = f'https://static-maps.yandex.ru/1.x/?ll={lat},{lon}&size=450,450&z={z}&l=map'
url = f'https://static-maps.yandex.ru/1.x/?l=map&bbox={west},{south}~{east},{north}'
response = requests.get(url)

with open('map_new.png', 'wb') as f:
    f.write(response.content)