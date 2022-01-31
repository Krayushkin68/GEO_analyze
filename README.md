# OSM Analyze
> ### The project is under development

### Small package for retrieving data from Open Street Map services.
## Allows to:
### - Retrieve information about the infrastructure of an object in a given radius around it
### - Save this information in osm(xml) format
### - Obtain an image of the study area with infrastructure elements marked on it


## Example
    from pygeoanalyze import Infrastructure
    
    inf = Infrastructure(address='Люберцы, Барыкина 8', search_range=800)
    if inf.analyze():
        print(inf.received_info)
        inf.save_to_xml('data/map.xml')
        inf.draw_map('data/map.png')
    
    inf = Infrastructure(lat=55.706315, lon=37.771571, search_range=800)
    if inf.analyze():
        print(inf.received_info)
        inf.save_to_xml('data/map2.xml')
        inf.draw_map('data/map2.png')
		
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
![map](https://user-images.githubusercontent.com/71232265/151858409-176051aa-8e22-4b6b-a502-d5f1291d1689.png)

