'''Testing the Hub class'''

from envrihub import Hub

def test_geo_search():
    geography = 'POLYGON((10.703125000000004 48.345191092562935,28.984375000000004 48.345191092562935,28.984375000000004 36.17766212248528,10.703125000000004 36.17766212248528,10.703125000000004 48.345191092562935))'
    hub = Hub()
    assert len(list(hub.search_catalogue(geography = geography)))>0, 'Geographic search from the Hub does not work'