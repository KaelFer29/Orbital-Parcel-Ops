from app.handlers import ops


def test_health_check():
    resp = ops.health_check({})
    assert resp['statusCode'] == 200
    assert 'status' in __import__('json').loads(resp['body'])
