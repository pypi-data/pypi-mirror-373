from collections.abc import Iterable
from envrihub.cos.catalogue import EposCatalogue
from envrihub.cos.models import Distribution
from envrihub.data_access.models import DataAccessObject
TEST_CATALOGUE_ADDRESS ='https://catalogue.staging.envri.eu/api/v1'

def test_distribution():
    cos =  EposCatalogue(TEST_CATALOGUE_ADDRESS )
    results = list(cos.search('beacon'))
    dist = cos.retrieve_resource(results[0].id)
    assert isinstance(dist, Distribution), f'{str(dist)} is not a Distribution object'

def test_distribution_dao():
    cos =  EposCatalogue(TEST_CATALOGUE_ADDRESS )
    results = list(cos.search('beacon'))
    dist = cos.retrieve_resource(results[0].id)
    assert dist.id == results[0].id, f'Catalogue returned id {str(dist.id)} which is different from the requested one'

def test_dao_access():
    cos =  EposCatalogue(TEST_CATALOGUE_ADDRESS )
    results = list(cos.search('marine species'))
    dist = cos.retrieve_resource(results[1].id)
    data = dist.dao.access()
    assert isinstance(data, Iterable), 'Unable to parse JSON. Probably connection does not work'

def test_catalogue_search_free_text():
    cos =  EposCatalogue(TEST_CATALOGUE_ADDRESS )
    results = list(cos.search('marine species'))
    assert len(results)>1, 'Catalogue does not find sh*t with free text search'

def test_catalogue_search_coords():
    cos =  EposCatalogue(TEST_CATALOGUE_ADDRESS )
    results = list(cos.search(bbox = (10.70, 36.17, 28.98, 48.34)))
    assert len(results)>1, 'Catalogue does not find sh*t with geo search'

def test_file_access_from_cos():
    cos =  EposCatalogue(TEST_CATALOGUE_ADDRESS )
    results = list(cos.search('beacon'))
    dist = cos.retrieve_resource(results[0].id)
    assert isinstance(dist.dao.access(), bytes), 'File access does not download bytes object'