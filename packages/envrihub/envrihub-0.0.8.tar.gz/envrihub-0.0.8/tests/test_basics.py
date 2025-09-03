## Datetime parsing
from datetime import datetime
import pytz
from envrihub.data_access.argo import to_argo_datetime
from envrihub.data_access.open_api_client import _to_parameter_name
from envrihub.data_access.seadatanet import to_seadatanet_datetime


def test_datetime_parsing_argo_outformat():
    t = to_argo_datetime(datetime(2024, 1, 23, 9, 21, 54, tzinfo=pytz.utc))
    target = '2024-01-23T09:21:54+00:00'
    assert t==target, f'Incorrectly parsed datetime, expected {target}, but got {t}'

def test_datetime_parsing_seadatanet_outformat():
    t = to_seadatanet_datetime(datetime(2024, 1, 23, 9, 21, 54, tzinfo=pytz.utc))
    target = '2024-01-23'
    assert t==target, f'Incorrectly parsed datetime, expected {target}, but got {t}'

def test_to_parameter_name():
    assert _to_parameter_name('Content-Type') == 'Content_Type', 'Parameter names are not not sanitized enough'