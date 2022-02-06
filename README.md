
# GEO Analyze
> ### The project is under development

### Small package for retrieving data from Open Street Map and Yandex Maps API services.
## Allows to:
### - Retrieve information about the infrastructure of an object in a given radius around it
### - Save this information in osm(xml) format
### - Obtain an image of the study area with infrastructure elements marked on it


## Example
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

		
### Result info
Dictionary containing the number of objects found in the category and their names (if any)

    {
    'food': [4, ['Пират пицца', 'Суши Фреш', 'Буханка', 'Venue']],
    'education': [5, ['Самолётик', 'Детский сад №15 «Бригантина»', 'Школа № 28', 'Детство']],
    'public_transport': [16, ['С/т Зенино', 'Улица Лавриненко', 'Зенинское шоссе', ...]],
    'personal_transport': [13, ['AquaService']],
    'finance': [3, ['Сбербанк']],
    'pharmacy': [7, ['Планета здоровья', 'Планета Здоровья', 'Социальная аптека', ...]],
    'entertainment': [0, []],
    'malls': [0, []],
    'supermarkets': [6, ['Винлаб', 'Магнит', 'Первым делом', 'Дикси', 'Пятёрочка']],
    'small_shops': [8, ['Гурман', 'ВкусВилл', 'Продукты', 'Минимаркет']]
    }

### Result map
![map_ya](https://user-images.githubusercontent.com/71232265/152334291-abd196b9-39d0-4daf-8574-e68fd56361ec.png)

