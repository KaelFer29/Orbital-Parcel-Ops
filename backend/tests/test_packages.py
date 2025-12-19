import json
import pytest
from unittest.mock import Mock, patch
from app.handlers import packages


@pytest.fixture
def mock_db_query():
    with patch('app.db.query') as mock:
        yield mock


def test_list_packages_success(mock_db_query):
    mock_db_query.return_value = [
        {'id': 1, 'tracking_number': 'PKG-001', 'status': 'pending'}
    ]
    
    event = {'queryStringParameters': {'limit': '10'}}
    resp = packages.list_packages(event)
    
    assert resp['statusCode'] == 200
    body = json.loads(resp['body'])
    assert len(body) == 1
    assert body[0]['tracking_number'] == 'PKG-001'


def test_get_package_not_found(mock_db_query):
    mock_db_query.return_value = None
    
    event = {'pathParameters': {'id': '999'}}
    resp = packages.get_package(event)
    
    assert resp['statusCode'] == 404


def test_create_package_success(mock_db_query):
    mock_db_query.return_value = [
        {'id': 1, 'tracking_number': 'PKG-NEW', 'status': 'pending'}
    ]
    
    event = {
        'body': json.dumps({
            'tracking_number': 'PKG-NEW',
            'origin': 'NYC',
            'destination': 'LA',
            'weight_kg': 2.5
        })
    }
    
    resp = packages.create_package(event)
    
    assert resp['statusCode'] == 201
    body = json.loads(resp['body'])
    assert body['tracking_number'] == 'PKG-NEW'


def test_create_package_missing_fields(mock_db_query):
    event = {'body': json.dumps({})}
    resp = packages.create_package(event)
    
    assert resp['statusCode'] == 400
