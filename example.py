from pygeoanalyze import Infrastructure

inf = Infrastructure(address='Люберцы, Барыкина 8', search_range=800)
if inf.analyze():
    print(inf.received_info)
    inf.save_to_xml('data/map.xml')
    inf.draw_map('data/map.png')

# inf = Infrastructure(lat=55.706315, lon=37.771571, search_range=800)
# if inf.analyze():
#     print(inf.received_info)
#     inf.save_to_xml('data/map2.xml')
#     inf.draw_map('data/map2.png')
