import envrihub
from envrihub.data_access.models import DataAccessObject, OpenAPI3DataAccess
from envrihub.data_access.open_api_client import build_access_class, recursion_limit_handler_void
from prance import ResolvingParser


def test_recursive_spec_parsing():
    parser = ResolvingParser('https://catalogue.staging.envri.eu/api/v1/openapi.json', recursion_limit_handler=recursion_limit_handler_void)
    parser.parse()
    specification = parser.specification
    assert isinstance(specification, dict), f'Parsed specfication is {type(specification)} instead of good ol dict'

def test_openapi_client():
    parser = ResolvingParser('https://catalogue.staging.envri.eu/api/v1/openapi.json', recursion_limit_handler=recursion_limit_handler_void)
    parser.parse()
    specification = parser.specification
    dao = build_access_class(specification, base_address='https://catalogue.staging.envri.eu/')()
    assert isinstance(dao, OpenAPI3DataAccess), 'Wrong DAO type found'

def test_openapi_client_call():
    parser = ResolvingParser('https://catalogue.staging.envri.eu/api/v1/openapi.json', recursion_limit_handler=recursion_limit_handler_void)
    parser.parse()
    specification = parser.specification
    dao = build_access_class(specification, base_address='https://catalogue.staging.envri.eu/')
    dao_instance = dao()
    result = dao_instance.resourcessearch(q='minchia')
    assert isinstance(result, dict), 'OpenAPI client does not manage to make a proper GET request'