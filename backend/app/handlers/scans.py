import json
from app import db, models


def record_scan(event):
    try:
        body = json.loads(event.get('body', '{}'))
        package_id = body.get('package_id')
        location = body.get('location')
        scan_type = body.get('scan_type', 'checkpoint')
        
        if not all([package_id, location]):
            return {'statusCode': 400, 'body': json.dumps({'error': 'Missing required fields'})}
        
        scan = models.create_scan(db.query, package_id, location, scan_type)
        return {
            'statusCode': 201,
            'body': json.dumps(dict(scan), default=str)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def list_scans(event):
    try:
        qs_params = event.get('queryStringParameters') or {}
        package_id = qs_params.get('package_id')
        
        if package_id:
            scans = models.get_scans_by_package(db.query, package_id)
        else:
            limit = int(qs_params.get('limit', 50))
            scans = models.list_recent_scans(db.query, limit)
        
        return {
            'statusCode': 200,
            'body': json.dumps([dict(s) for s in scans], default=str)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
