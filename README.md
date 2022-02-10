
# GEO Analyze
> ### The project is under development

### Small package for retrieving data from Open Street Map and Yandex Maps API services.
## Allows to:
### - Retrieve information about the infrastructure of an object in a given radius around it
### - Save this information in osm(xml) and json formats
### - Obtain an image of the study area with infrastructure elements marked on it

**Note.** To use the Yandex analyzer, you need to get an API token.


## Example
    from pygeoanalyze import Infrastructure  
    import json  
      
    TOKEN = json.load(open('token.json', 'rt')).get('TOKEN')  
      
    inf_osm = Infrastructure(address='Люберцы, Барыкина 8', search_range=800, source='OSM')  
    if inf_osm.analyze():  
        print(inf_osm.received_info)  
        inf_osm.save_to_xml('data/map_osm.xml')  
        inf_osm.save_to_json('data/map_osm.json')  
        inf_osm.draw_map('data/map_osm.png')  
      
    inf_ya = Infrastructure(address='Люберцы, Барыкина 8', search_range=500, source='Yandex', token=TOKEN)  
    if inf_ya.analyze():  
        print(inf_ya.received_info)  
        inf_ya.save_to_json('data/map_ya.json')  
        inf_ya.draw_map('data/map_ya.png')


		
### Result info
Json containing the number, names,  and coordinates of found objects grouped by categories

    [  
      {  
      "category": "food",  
      "count": 6,  
      "items": [  
         {  
           "name": "Жан Руа",  
           "address": "Вертолётная ул., 4/2, Люберцы, Россия",  
           "coordinates": [37.958793, 55.706957]  
         },  
         {  
           "name": "СтритФуд",  
           "address": "ул. Барыкина, 2, Люберцы, Россия",  
           "coordinates": [37.955729, 55.707104]  
         },  
	      ...  
        ]  
      },  
      {  
      "category": "education",  
      "count": 10,  
      "items": [  
         {  
           "name": "Средняя общеобразовательная школа № 28",  
           "address": "Вертолётная ул., 8, Люберцы, Россия",  
           "coordinates": [37.960052, 55.706352]  
         },  
	     {  
           "name": "Детский сад на Барыкина",  
           "address": "ул. Барыкина, 6, Люберцы, Россия",  
           "coordinates": [37.957828, 55.707228]  
         },  
	      ...  
        ]  
      },
      ...  
    ]

### Result map
![map_ya](https://user-images.githubusercontent.com/71232265/152334291-abd196b9-39d0-4daf-8574-e68fd56361ec.png)

