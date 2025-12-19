import json
import pytest
from unittest.mock import patch
from app.handlers import scans


@pytest.fixture
def mock_db_query():
    with patch('app.db.query') as mock:
        yield mock


def test_record_scan_success(mock_db_query):
    mock_db_query.return_value = [
        {'id': 1, 'package_id': 1, 'location': 'NYC Hub', 'scan_type': 'checkpoint'}
    ]
    
    event = {
        'body': json.dumps({
            'package_id': 1,
            'location': 'NYC Hub',
            'scan_type': 'checkpoint'
        })
    }
    
    resp = scans.record_scan(event)
    
    assert resp['statusCode'] == 201
    body = json.loads(resp['body'])
    assert body['location'] == 'NYC Hub'


def test_record_scan_missing_fields(mock_db_query):
    event = {'body': json.dumps({})}
    resp = scans.record_scan(event)
    
    assert resp['statusCode'] == 400


def test_list_scans_all(mock_db_query):
    mock_db_query.return_value = [
        {'id': 1, 'location': 'NYC Hub'},
        {'id': 2, 'location': 'LA Hub'}
    ]
    
    event = {'queryStringParameters': {}}
    resp = scans.list_scans(event)
    
    assert resp['statusCode'] == 200
    body = json.loads(resp['body'])
    assert len(body) == 2


def test_list_scans_by_package(mock_db_query):
    mock_db_query.return_value = [
        {'id': 1, 'package_id': 1, 'location': 'NYC Hub'}
    ]
    
    event = {'queryStringParameters': {'package_id': '1'}}
    resp = scans.list_scans(event)
    
    assert resp['statusCode'] == 200
    body = json.loads(resp['body'])
    assert len(body) == 1
    assert body[0]['package_id'] == 1
